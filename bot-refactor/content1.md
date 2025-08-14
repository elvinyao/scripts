1.背景1
有一套系统，用途是从oracle apex的restapi获取任务，然后根据任务里的设置调用jira，confluence和mattermost进行jira票的数据获取，数据加工等所需要的业务处理，最终将所需要的结果反应在jira，confluence上，此外有一些还需要通过mattermost发送通知。

2.背景2
目前，另外一个团队，设计了一套，由10个业务bot和4个中间件service ticket-service,wiki-service,mattermost-service和auth-service组成的系统。

各个业务bot从oracle apex的restapi每3s获取任务，然后这些bot会调用ticket-service,wiki-service,mattermost-service和auth-service这些中间service，进行业务的操作完成用户所需要的业务，最终还需要定时每3s将用户的处理进度通过restapi更新到oracle apex里去。

这10个业务bot分3类：
1.批量注册类： task-imp, task-exp, case-imp, case-exp和indication-imp
task-imp, task-exp会调用 ticket-service和ticket-service。这2个bot的操作对象类型是jira的 Task类型的issueType。这个类型名称不要hardcoding，是可以通过程序config进行配置的
task-imp会根据从api获取到的用户的Excel文件，按照规则，将excel内容进行处理，首先通过auth-service验证用户有没有权限。其次再通过ticket-service把excel的内容,将它新增更新或者删除到jira上。 然后task-exp这个业务Bot会也是同样读取用户在Oracle Apex DB上的任务，任务本身不包括excel,首先通过auth-service验证用户有没有权限,是bot将这个任务条件通过TicketService获取相应的jira的数据,然后将这些数据按照模板生成一个Excel文件,然后将这个Excel文件更新到Oracle Apex里面去。

CaseImport和CaseExport跟TaskImport和TaskExport非常的類似, 它也是會調用ticket-service和ticket-service, 但是這兩個bot的操作對象是需要的Case表和Case內顯。 然後這個類型不是通過hardcoding的, 而是首先在程序的Config裡是有默認的配置, 然後用戶會在Excel的設置的Sheet裡, 可以定義他想使用的這兩個issuetype。 
操作邏輯上講, CaseImport也是從API獲取到用戶的Excel文件處理, 然後通過AuthService驗證有沒有權限, 然後再通過這個Service把Excel內容進行新增、更新或者刪除到機台上。 然後CaseExport的用戶也是獨立用戶在Oracle App上。 這個任務本身的API取得的內容不包括Excel, 也是通過AuthService驗證用戶有沒有權限, 然後獲得將這個任務條件通過CaseImport的Service獲取到機台數據, 然後也是將這些數據模擬生成為Excel文件, 最後將這個文件更新到Oracle App上去。





2.通知类： notice-set, analysis-set, update-set
3.状况把握类： pr-set, qe-set

Python 开发的 Bot 工具，集成 JIRA、Confluence 和 Mattermost API，提供以下核心能力：

任务管理：读取并分发任务、执行业务逻辑、通知结果
数据检索：基于 JQL（JIRA Query Language）或 Confluence 页面内容进行查询，或者指定某个API进行查询
自动通知：通过 Mattermost等渠道自动推送通知

需要将操作 jira 和 confluence 和mattermost的作为中间service。 以达到如下功能。 所有基础的jira api的调用，都使用jira 中间service，但是关于jira实际获取到的数据的逻辑操作，都在这10个各自的bot里。只把共用的部分放在jira middle service里。再次，这些10个bot，调用jira，需要完成很多jira ticket get， post，put，delete等等各种操作。需要对这些10个bot对jira的操作，统一由jira middle service进行流量限制。 最初是一个较高的rate，如果发现有错误，则降低速率，如果一段时间没有错误，则恢复速率这种形式。 
而且，这10个业务bot，都调用1个jira middle servi
 
请帮我整理上面的架构需求说明，以及架构设计图。


需求，release停机，不对别的bot有影响
