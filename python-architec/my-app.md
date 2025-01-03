



1. 想要对现有的一个读取APEX API的配置内容，然后执行所要求的业务，操作jira和confluence api的程序进行重构。APEX API的配置内容， 会有定时执行的task，也会有即时执行的task。
task，包括定时的时间（包括营业日，周末等），每月第几天，每周第几天等等这种配置。
读取APEX API的配置内容，这个是不是要一个独立的module去处理。可以暂定为定时3s去读取api里设置的未处理状态的即时task信息。 
同时，还要处理读取定时处理的task，并采取一个好的方式去保存和处理。
并且主程序在处理完成之后，要把处理状态更新回apex api的db里面去。


2.
操作jira的类型，包括批量新增jira issue，批量更新。以及将jira ticket的一些field的内容更新在confluence page上。
关于jira 和 confluence 以及mattermost的登陆状态，建立的http client如何在不同的线程里进行共享
3.
task执行后到一些通知消息会发送到mattermost里。


需要考虑的方面：
1.因为会同时操作比较多的jira 和 confluence api，所以需要采用多线程的方式来分别执行多个task。 此外每个task内可能会包括多个jira ticket的操作，所以还需要再进行多线程的操作。

2. 被调用的jira 或者confluence api有流量限制，所以需要在程序调用api 发生异常的时候，进行发送的流量控制，比如让线程暂停1s在再发送。如果暂停1s还是异常，那么就暂停2s，这么类推，最多暂停5s。


3.要考虑定时执行和及时执行应该怎么实现。

4.然后是关于读取apex api的task的多线程，以及每个task内如果涉及api操作的时候再进行多线程的处理，这些多线程如何控制以及共享数据和维护状态。

5.再就是关于作为客户端，整体控制所有线程的api 发生异常时候进行流量控制。
6.然后就是设计中不要使用异步的机制，因为调用API都得是同步的方式调用API，使用多线程来增加执行效率


根据您提供的信息，我为您整理了以下IT需求：

1. 系统架构
	• 创建一个独立的模块来处理APEX API的配置内容读取
	• 主程序负责任务调度和执行
	• 使用多线程处理多个任务和API调用
2. APEX API配置读取模块
	• 定期（每3秒）读取即时任务信息
	• 读取和处理定时任务信息
	• 设计高效的数据结构来存储和管理任务信息
3. 任务执行模块
	• 支持批量新增和更新Jira issue
	• 更新Confluence页面内容
	• 发送通知消息到Mattermost
4. 多线程实现
	• 为每个任务创建单独的线程
	• 在任务内部使用多线程处理多个Jira ticket操作
	• 实现线程间的数据共享和状态维护
5. API调用管理
	• 实现API调用的流量控制机制
	• 在遇到异常时实现指数退避重试策略
	• 共享HTTP客户端以维护登录状态
6. 任务调度
	• 实现定时任务和即时任务的调度机制
	• 确保定时任务按照指定的时间（包括营业日、周末、每月第几天、每周第几天等）执行
7. 状态更新
	• 任务执行完成后，更新APEX API数据库中的处理状态
8. 异常处理
	• 实现健壮的异常处理机制，确保程序能够正常运行并从错误中恢复
9. 性能优化
	• 使用多线程提高执行效率
	• 优化数据结构和算法以提高性能
10. 同步调用
	• 确保所有API调用都是同步的，不使用异步机制
11. 可扩展性
	• 设计模块化的结构，以便于未来添加新功能或支持新的API
12. 日志和监控
	• 实现详细的日志记录，以便于调试和问题排查
	• 添加监控机制，以跟踪系统性能和任务执行状态

这些需求涵盖了您描述的主要功能和考虑因素。在实现过程中，您可能需要进一步细化某些需求，并考虑其他因素如安全性、可维护性等。


这个演示程序包含以下组件：

1. ApexConfigReader: 模拟从APEX API读取配置的模块。
2. ApiClient: 处理API调用和重试逻辑的客户端。
3. JiraOperator, ConfluenceOperator, MattermostOperator: 模拟各种API操作的模块。
4. TaskExecutor: 执行任务的模块。
5. MainProgram: 主程序，协调所有其他模块的工作。

程序的主要流程：

1. 主程序初始化所有必要的组件。
2. 启动两个线程：一个用于读取配置，另一个用于执行任务。
3. 配置读取线程每3秒从APEX API读取一次配置。
4. 任务执行线程持续检查是否有新的即时任务或到期的定时任务，并为每个任务创建一个新的线程来执行。
5. 每个API调用都有重试逻辑，在失败时会逐渐增加重试间隔。

这个演示程序提供了一个基本的框架，展示了如何组织和协调不同的模块。在实际应用中，您需要用实际的API调用和业务逻辑替换这些模拟的操作。此外，您可能还需要添加更多的错误处理、日志记录和监控功能。
