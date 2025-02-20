---
title: 📖 34｜并发处理（下）：从atomics到Channel，Rust都提供了什么工具？
createdAt: 2024-10-07 16:33
notebook: "[[🗂️ Rust 编程第一课]]"
allDay: 
startTime: 
endTime: 
date: 2024-10-07
project: 
area: 
resource: 
archived: 
tags:
  - "#note/🌱"
  - "#readwise"
links: 
due: 2024-10-07
nextReview: 2024-10-14
status: "#processing"
---

# 原文摘要
> [!tip] 
> 将原始文章中的较为重要的信息「摘录」到笔记当中，对一些稍微重要的信息进行「加粗处理」（用一对 ** 包裹着内容），在未来「回看笔记」时快速理解第一层信息

对于并发状态下这三种常见的工作模式：自由竞争模式、map/reduce 模式、DAG 模式，我们的难点是如何在这些并发的任务中进行同步。atomic / Mutex 解决了自由竞争模式下并发任务的同步问题，也能够很好地解决 map/reduce 模式下的同步问题，因为此时同步只发生在 map 和 reduce 两个阶段。

![[Pasted image 20241007163456.png]]
然而，它们没有解决一个更高层次的问题，也就是 DAG 模式：如果这种访问需要按照一定顺序进行或者前后有依赖关系，该怎么做？这个问题的典型场景是**生产者 - 消费者模式：生产者生产出来内容后，需要有机制通知消费者可以消费**。比如 socket 上有数据了，通知处理线程来处理数据，处理完成之后，再通知 socket 收发的线程发送数据。

## 1. `Condvar`
所以，操作系统还提供了 `Condvar`. `Condvar` 有两种状态
- 等待（wait）：线程在队列中等待，直到满足某个条件。
- 通知（notify）：当 `condvar` 的条件满足时，当前线程通知其他等待的线程可以被唤醒。通知可以是单个通知，也可以是多个通知，甚至广播（通知所有人）。

在实践中，`Condvar` 往往和 `Mutex` 一起使用：**`Mutex` 用于保证条件在读写时互斥，`Condvar` 用于控制线程的等待和唤醒**。我们来看一个例子：

```rust
use std::{
    sync::{Arc, Condvar, Mutex},
    thread,
    time::Duration,
};

fn main() {
    let pair = Arc::new((Mutex::new(false), Condvar::new()));
    let pair2 = Arc::clone(&pair);

    thread::spawn(move || {
        let (lock, cvar) = &*pair2;
        let mut started = lock.lock().unwrap();
        *started = true;
        eprintln!("I'm a happy worker!");
        // 通知主线程
        cvar.notify_one();
        loop {
            thread::sleep(Duration::from_secs(1));
            println!("working...");
        }
    });

    // 等待工作线程的通知
    let (lock, cvar) = &*pair;
    let mut started = lock.lock().unwrap();
    while !*started {
        started = cvar.wait(started).unwrap();
    }
    eprintln!("Worker started!");
}
```

这段代码通过 `condvar`，我们实现了 `worker` 线程在执行到一定阶段后通知主线程，然后主线程再做一些事情。

这里，我们使用了一个 `Mutex` 作为互斥条件，然后在 `cvar.wait()` 中传入这个 `Mutex`。这个接口需要一个 `MutexGuard`，以便于知道需要唤醒哪个 `Mutex` 下等待的线程：

```rust
pub fn wait<'a, T>(
	&self,
	guard: MutexGurad<'a, T>
) -> LockResult<MutexGurad<'a, T>>
```

## 2. Channel
但是用 `Mutex` 和 `Condvar` 来处理复杂的 DAG 并发模式会比较吃力。所以， Rust 还提供了各种各样的 Channel 用于处理并发任务之间的通讯。

**Channel 把锁封装在了队列写入和读取的小块区域内，然后把读者和写者完全分离**，使得读者读取数据和写者写入数据，对开发者而言，除了潜在的上下文切换外，完全和锁无关，就像访问一个本地队列一样。所以，对于大部分并发问题，我们都可以用 Channel 或者类似的思想处理 (比如 actor model).

Channel 在具体哦实现的时候，根据不同的使用场景，会选择不同的工具。

Rust 提供了以下四种 Channel:
- `oneshot`: 这可能是最简单的 Channel，写者就只发一次数据，而读者也只读一次。这种一次性的、多个线程间的同步可以用 `oneshot` channel 完成。由于 `oneshot` 特殊的用途，实现的时候可以直接用 atomic swap 来完成。
- `rendezvous`: 很多时候，我们只需要通过 Channel 来控制线程间同步，并不需要发送数据。`rendezvous` channel 是 channel size 为 0 的一种特殊情况。这种情况下，我们用 `Mutex` + `Condvar` 实现就足够了，在具体实现中，`rendezvous` channel 其实也是 `Mutex`  + `Condvar` 的一个包装。
- `bounded`: **`bounded` channel 有一个队列，但队列有上限。一旦队列被写满了，写者也需要被挂起等待**。当阻塞发生后，读者一旦读取数据，channel 内部就会使用 `Condvar` 的 `notify_one` 通知写者，唤醒某个写者使其能够继续写入。因此，实现中，一般会用到 `Mutex` + `Condvar` + `VecDeque` 来实现；如果不用 `Condvar`，可以直接使用 `thread::park` + `thread::notify` 来完成（[flume](https://github.com/zesterer/flume) [GitHub - zesterer/flume: A safe and fast multi-producer, multi-consumer channel.](https://github.com/zesterer/flume)的做法）；如果不用 `VecDeque`，也可以使用双向链表或者其它的 ring buffer 的实现。
- `unbounded`：queue 没有上限，如果写满了，就自动扩容。我们知道，Rust 的很多数据结构如 `Vec` 、`VecDeque` 都是自动扩容的。`unbounded` 和 `bounded` 相比，除了不阻塞写者，其它实现都很类似。
所有这些 channel 类型，同步和异步的实现思路大同小异，主要的区别在于挂起 / 唤醒的对象。在同步的世界里，挂起 / 唤醒的对象是线程；而异步的世界里，是粒度很小的 task。

根据 Channel 读者和写者的数量，Channel 又可以分为：
- `SPSC`：Single-Producer Single-Consumer，单生产者，单消费者。最简单，可以不依赖于 Mutex，只用 atomics 就可以实现。
- `SPMC`：Single-Producer Multi-Consumer，单生产者，多消费者。需要在消费者这侧读取时加锁。
- `MPSC`：Multi-Producer Single-Consumer，多生产者，单消费者。需要在生产者这侧写入时加锁。
- `MPMC`：Multi-Producer Multi-Consumer。多生产者，多消费者。需要在生产者写入或者消费者读取时加锁。
在众多 Channel 类型中，使用最广的是 `MPSC` channel，多生产者，单消费者，因为往往我们希望通过单消费者来保证，用于处理消息的数据结构有独占的写访问。
![[Pasted image 20241012100550.png]]
比如，在 [xunmi](https://github.com/tyrchen/xunmi/blob/master/src/indexer.rs#L50)[xunmi/src/indexer.rs at master · tyrchen/xunmi · GitHub](https://github.com/tyrchen/xunmi/blob/master/src/indexer.rs#L50) 的实现中，`index writer` 内部是一个多线程的实现，但在使用时，我们需要用到它的可写引用。如果要能够在各种上下文中使用 `index writer`，我们就不得不将其用 `Arc<Mutex<T>>` 包裹起来，但这样在索引大量数据时效率太低，所以我们可以用 `MPSC` channel，让各种上下文都把数据发送给单一的线程，使用 `index writer` 索引，这样就避免了锁：

```rust
pub struct IndexInner {
	index: Index,
	reader: IndexReader,
	config: IndexConfig,
	updater: Send<Input>
}

pub struct IndexUpdater {
	sender: Sender<Input>,
	t2s: bool,
	schema: Schema
}

impl Indexer {
	// 打开或创建一个 index
	pub fn open_or_create(config: IndexConfig) -> Result<Self> {
		let schema = config.schema.clone();
		let index = if let Some(dir) = &config.path {
			fs::create_dir_all(dir)?;
			let dir = MmapDirectory::open(dir)?;
			Index::open_or_create(dir, schema.clone())?
		} else {
			Index::create_in_ram(schema.clone())
		};

		Self::set_tokenize(&index, &config);

		let mut writer = index.writer(config.write_memory)?;

		// 创建一个 unbound MPSC channel
		let (s, r) = unbounded::<Input>();

		// 启动一个线程，从 channel 的 reader 中读取数据
		thread::spawn(move || {
			for input in r {
				// 然后用 index writer 处理这个 input
				if let Err(e) = input.process(&mut writer, &schema) {
					warn!("Failed to process input. Error: {:?}", e);
				} 
			}
		});

		Self::new(index, config, s)
	}
}
```


# 重点摘要
> [!tip] 
> 在完成「第一层：原文摘要」后马上就整理「第二层：重点摘要」，虽然需要遵循「不同的时间段完成不同层级」的规则，但是在阅读或整理笔记的当下，如果觉得有些内容需要重点标注，需要第一时间将「第一层」内容拷贝到「第二层」进行「重点标注」，同时如果有必要也可以添加自己的「注释」，方便进行辅助理解

# 长青笔记
> [!tip]
>  常青笔记，也称为永久笔记。如果当前笔记的阅读让你产生了新的灵感，站在「原始素材」的基础上写一篇文章，然后通过「双向链接」将笔记添加到「第三层：常青笔记」中

# 闪念
> [!tip]
> 这一层主要存放那些「灵光一现」的内容，当阅读笔记的当下突然某一段内容产生了一些灵感，随手记录在「第四层」，并设置好标签「闪念胶囊」方便将来索引

# 回归问题
> [!tip] 
> 使用几个问题，将本笔记内容核心知识提炼出来