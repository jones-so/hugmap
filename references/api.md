# 巨图引擎 API 参考

Skill 与 API 共用接口和 X-API-Key。免 Key 按公网 IP、带 Key 按账号，各自每天 100 次，北京时间零点重置。网站会话不占用外部额度。成功业务请求扣次，失败不扣。个人关注必须带 Key。

服务地址：https://www.hugmap.com
网页文档：https://www.hugmap.com/developers

## GET /api/v1/opportunities

检索公告

沿用网站统一字典和筛选逻辑。仅返回已授权且可公开的真实公告，列表不包含正文；正文和附件通过详情接口读取。每页是一次业务调用。

| 参数 | 位置 | 类型 | 说明 |
| --- | --- | --- | --- |
| query | query | string | 关键词，搜索项目、采购人及需求 |
| region | query | string | 省级地区编码或兼容中文名称；从字典 region 获取 |
| category | query | string | 采购品类编码；父品类包含全部下级，支持多品类公告匹配 |
| stage | query | string | 招标阶段字典编码 |
| procurementMethod | query | string | 采购方式字典编码，独立于招标阶段 |
| noticeType | query | string | 兼容旧参数：阶段名称或采购方式；不建议与 stage 冲突使用 |
| tenderType | query | string | 招标类型字典编码 |
| buyerType | query | string | 实际采购人单位类型字典编码 |
| publishedRange | query | string | 发布时间快捷选项，取自 publishedRange 字典；日期按北京时间计算 |
| publishedFrom | query | string | 起始发布日期，包含当天；YYYY-MM-DD |
| publishedTo | query | string | 结束发布日期，包含当天；YYYY-MM-DD |
| deadlineRange | query | string | 投标截止快捷选项，取自 deadlineRange 字典 |
| deadlineFrom | query | string | 截止日期下界，包含当天；YYYY-MM-DD |
| deadlineTo | query | string | 截止日期上界，包含当天；YYYY-MM-DD |
| deadlineMissing | query | boolean | 是否仅查询未公布截止日期的公告 |
| budgetRange | query | string | 预算快捷选项，取自 budgetRange 字典 |
| budgetMin | query | number | 预算下界（人民币元），包含边界 |
| budgetMax | query | number | 预算上界（人民币元），不包含边界 |
| cursor | query | string | 上一页返回的 nextCursor；后续请求保持相同筛选和 limit，不自行构造 |
| limit | query | integer | 每页条数，默认 25，最多 100 |

- 200：成功
- 400：筛选、日期或游标无效，不扣次数
- 401：Key 无效、已撤销，或个人关注未提供 Key，不扣次数
- 404：项目或附件不存在，不扣次数
- 429：当日额度用尽；匿名请传 Key，账号请等待北京时间零点重置；不自动重试
- 502：附件下载地址或源站暂不可用，不扣次数
- 503：服务暂不可用，不扣次数

## GET /api/v1/opportunities/{id}

读取完整详情

免费额度内无需登录或 Key，返回已同步的完整正文、官方来源和附件。历史别名会解析到规范公告。源站无正文或仍在同步会通过 contentStatus 说明，不承诺不存在的正文。

| 参数 | 位置 | 类型 | 说明 |
| --- | --- | --- | --- |
| id | path | string | 项目 ID |

- 200：成功
- 400：筛选、日期或游标无效，不扣次数
- 401：Key 无效、已撤销，或个人关注未提供 Key，不扣次数
- 404：项目或附件不存在，不扣次数
- 429：当日额度用尽；匿名请传 Key，账号请等待北京时间零点重置；不自动重试
- 502：附件下载地址或源站暂不可用，不扣次数
- 503：服务暂不可用，不扣次数

## GET /api/v1/opportunities/{id}/attachments/{attachmentId}/download

下载附件或获取下载地址

直接下载推荐 redirect=true。OSS 签名链接短期有效，不持久缓存。源站要求验证时返回官方入口，需要用户完成源站验证；不绕过访问控制。跨域重定向不得携带 Key。

| 参数 | 位置 | 类型 | 说明 |
| --- | --- | --- | --- |
| id | path | string | 项目 ID |
| attachmentId | path | string | 附件 ID，取自详情 attachments |
| redirect | query | boolean | true：返回 302 或文件流；false：返回 JSON 下载地址。签发地址扣一次，后续访问该地址不重复扣次；proxy 模式返回五分钟有效的一次性站内交付地址，原样访问即可，不需要再传 Key。 |

- 200：成功
- 302：跳转至 OSS 临时签名地址或官方附件地址，本请求扣 1 次
- 400：筛选、日期或游标无效，不扣次数
- 401：Key 无效、已撤销，或个人关注未提供 Key，不扣次数
- 404：项目或附件不存在，不扣次数
- 429：当日额度用尽；匿名请传 Key，账号请等待北京时间零点重置；不自动重试
- 502：附件下载地址或源站暂不可用，不扣次数
- 503：服务暂不可用，不扣次数

## GET /api/v1/dictionaries

获取统一字典

返回发布版本及地区、品类树、阶段、采购方式、招标类型、单位类型、发布时间、截止时间和预算选项。按版本缓存，避免每次检索都消耗额度。

- 200：成功
- 400：筛选、日期或游标无效，不扣次数
- 401：Key 无效、已撤销，或个人关注未提供 Key，不扣次数
- 404：项目或附件不存在，不扣次数
- 429：当日额度用尽；匿名请传 Key，账号请等待北京时间零点重置；不自动重试
- 502：附件下载地址或源站暂不可用，不扣次数
- 503：服务暂不可用，不扣次数

## GET /api/v1/metrics

查询统计指标

与网站趋势及首页使用相同统计；仅返回汇总，不公开来源目录或运营配置。

- 200：成功
- 400：筛选、日期或游标无效，不扣次数
- 401：Key 无效、已撤销，或个人关注未提供 Key，不扣次数
- 404：项目或附件不存在，不扣次数
- 429：当日额度用尽；匿名请传 Key，账号请等待北京时间零点重置；不自动重试
- 502：附件下载地址或源站暂不可用，不扣次数
- 503：服务暂不可用，不扣次数

## GET /api/v1/usage

查询当前身份额度

不扣调用次数。无 Key 返回当前公网 IP 额度，有 Key 返回所属账号额度；无效 Key 返回 401。

- 200：成功
- 400：筛选、日期或游标无效，不扣次数
- 401：Key 无效、已撤销，或个人关注未提供 Key，不扣次数
- 404：项目或附件不存在，不扣次数
- 429：当日额度用尽；匿名请传 Key，账号请等待北京时间零点重置；不自动重试
- 502：附件下载地址或源站暂不可用，不扣次数
- 503：服务暂不可用，不扣次数

## GET /api/v1/watchlist

查询个人关注

按添加时间倒序返回当前 Key 所属账号的关注项目摘要，与网站账号同步。

| 参数 | 位置 | 类型 | 说明 |
| --- | --- | --- | --- |
| cursor | query | string | 上一页返回的 nextCursor；后续请求保持相同筛选和 limit，不自行构造 |
| limit | query | integer | 每页条数，默认 25，最多 100 |

- 200：成功
- 400：筛选、日期或游标无效，不扣次数
- 401：Key 无效、已撤销，或个人关注未提供 Key，不扣次数
- 404：项目或附件不存在，不扣次数
- 429：当日额度用尽；匿名请传 Key，账号请等待北京时间零点重置；不自动重试
- 502：附件下载地址或源站暂不可用，不扣次数
- 503：服务暂不可用，不扣次数

## PUT /api/v1/watchlist/{id}

关注项目

仅操作 Key 所属账号。操作幂等，成功请求每次计 1 次；添加前先解析公告别名，不重复创建关注。

| 参数 | 位置 | 类型 | 说明 |
| --- | --- | --- | --- |
| id | path | string | 项目 ID |

- 200：成功
- 400：筛选、日期或游标无效，不扣次数
- 401：Key 无效、已撤销，或个人关注未提供 Key，不扣次数
- 404：项目或附件不存在，不扣次数
- 429：当日额度用尽；匿名请传 Key，账号请等待北京时间零点重置；不自动重试
- 502：附件下载地址或源站暂不可用，不扣次数
- 503：服务暂不可用，不扣次数

## DELETE /api/v1/watchlist/{id}

取消关注

仅操作 Key 所属账号。操作幂等，成功请求每次计 1 次；添加前先解析公告别名，不重复创建关注。

| 参数 | 位置 | 类型 | 说明 |
| --- | --- | --- | --- |
| id | path | string | 项目 ID |

- 200：成功
- 400：筛选、日期或游标无效，不扣次数
- 401：Key 无效、已撤销，或个人关注未提供 Key，不扣次数
- 404：项目或附件不存在，不扣次数
- 429：当日额度用尽；匿名请传 Key，账号请等待北京时间零点重置；不自动重试
- 502：附件下载地址或源站暂不可用，不扣次数
- 503：服务暂不可用，不扣次数

## GET /api/v1/attachment-deliveries/{ticket}

使用一次性附件交付凭据

仅用于 download?redirect=false 返回的 proxy 地址。获取该地址时已扣次，此请求不再扣次；凭据五分钟过期且只能使用一次。不要自行构造。

| 参数 | 位置 | 类型 | 说明 |
| --- | --- | --- | --- |
| ticket | path | string | 下载接口返回地址中的一次性凭据 |

- 200：附件文件流
- 302：官方或 OSS 下载跳转
- 410：凭据过期或已使用

## 返回结构

### Opportunity

- `id`：规范公告 ID
- `title`：公告标题
- `buyer`：实际采购人
- `region`：地区名称
- `category`：主品类名称
- `noticeType`：招标阶段名称
- `summary`：项目摘要
- `requirements`：采购需求
- `sourceName`：官方来源名称
- `sourceUrl`：官方公告地址
- `sourceContentHtml`：已清理的官方 HTML 正文；为空时可读取 sourceContentText
- `sourceContentText`：正文纯文本
- `contentStatus`：正文同步状态，如已同步、源站无正文或待同步；以实际返回为准
- `stageCode`：标准阶段编码
- `procurementMethodCode`：标准采购方式编码
- `procurementMethod`：采购方式名称
- `buyerTypeCode`：标准单位类型编码
- `buyerType`：单位类型名称
- `regionCode`：标准省级地区编码
- `publishedAt`：ISO 8601 时间，可能为空
- `updatedAt`：ISO 8601 时间，可能为空
- `contentFetchedAt`：ISO 8601 时间，可能为空
- `classificationUpdatedAt`：ISO 8601 时间，可能为空
- `budget`：人民币元；null 表示未提供，不是零
- `deadline`：投标截止日期；未提供时为空
- `confidence`：数据置信度
- `sampleData`：是否为样例数据
- `classificationVersion`：integer,null
- `categories`：多个采购品类
- `tenderTypes`：多个招标类型
- `attachments`：array

### Label

- `code`：string
- `name`：string

### Attachment

- `id`：string
- `name`：string
- `url`：官方附件地址
- `downloadUrl`：站内交付地址；可能是兼容路径，Key 及额度规则相同
- `contentType`：媒体类型
- `position`：integer
- `archiveStatus`：归档状态，不影响可用官方附件交付
- `archivedSize`：integer,null

### SearchResult

- `items`：array
- `nextCursor`：string,null
- `total`：integer
- `sampleData`：boolean

### Error

- `error`：string

### Usage

- `used`：integer
- `quota`：integer
- `remaining`：integer
- `period`：string
- `resetAt`：string

### Dictionaries

- `version`：integer
- `catalogSource`：string
- `entries`：array

### DictionaryEntry

- `dimension`：string
- `code`：string
- `name`：string
- `parent`：string,null
- `sort`：integer
- `enabled`：boolean
- `mergedInto`：string,null
- `aliases`：array
- `values`：object

### Metrics

- `records`：integer
- `highConfidenceRecords`：integer
- `sources`：integer
- `sampleData`：boolean
- `coverage`：array
- `collectionMode`：string
- `categoryCounts`：array
- `regionCounts`：array
