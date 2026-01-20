package common

// HTTP 状态码常量
const (
	// 成功
	CodeSuccess = 200

	// 客户端错误 4xx
	CodeBadRequest          = 400
	CodeUnauthorized        = 401
	CodeForbidden           = 403
	CodeNotFound            = 404
	CodeMethodNotAllowed    = 405
	CodeConflict            = 409
	CodeUnprocessableEntity = 422
	CodeTooManyRequests     = 429

	// 服务器错误 5xx
	CodeInternalServerError = 500
	CodeNotImplemented      = 501
	CodeBadGateway          = 502
	CodeServiceUnavailable  = 503
	CodeGatewayTimeout      = 504
)

// 业务错误码常量
const (
	// 通用错误 1xxx
	ErrInvalidParams     = 1001
	ErrDatabaseError     = 1002
	ErrRecordNotFound    = 1003
	ErrRecordExists      = 1004
	ErrInvalidOperation  = 1005
	ErrPermissionDenied  = 1006

	// 项目相关错误 2xxx
	ErrProjectNotFound   = 2001
	ErrProjectExists     = 2002
	ErrProjectInvalid    = 2003

	// 模块相关错误 3xxx
	ErrModuleNotFound    = 3001
	ErrModuleExists      = 3002
	ErrModuleInvalid     = 3003
	ErrModuleCircular    = 3004

	// PRD 相关错误 4xxx
	ErrPRDNotFound       = 4001
	ErrPRDExists         = 4002
	ErrPRDInvalid        = 4003
	ErrPRDVersionInvalid = 4004

	// 测试用例相关错误 5xxx
	ErrTestCaseNotFound  = 5001
	ErrTestCaseExists    = 5002
	ErrTestCaseInvalid   = 5003
	ErrTestStepInvalid   = 5004

	// 标签相关错误 6xxx
	ErrTagNotFound       = 6001
	ErrTagExists         = 6002
	ErrTagInvalid        = 6003

	// 文件相关错误 7xxx
	ErrFileUploadFailed  = 7001
	ErrFileNotFound      = 7002
	ErrFileInvalid       = 7003
	ErrFileTooLarge      = 7004

	// 向量数据库相关错误 8xxx
	ErrVectorSyncFailed  = 8001
	ErrVectorSearchFailed = 8002
	ErrVectorNotFound    = 8003
)

// 错误消息映射
var ErrorMessages = map[int]string{
	// 通用错误
	ErrInvalidParams:     "Invalid parameters",
	ErrDatabaseError:     "Database error",
	ErrRecordNotFound:    "Record not found",
	ErrRecordExists:      "Record already exists",
	ErrInvalidOperation:  "Invalid operation",
	ErrPermissionDenied:  "Permission denied",

	// 项目相关错误
	ErrProjectNotFound:   "Project not found",
	ErrProjectExists:     "Project already exists",
	ErrProjectInvalid:    "Invalid project data",

	// 模块相关错误
	ErrModuleNotFound:    "Module not found",
	ErrModuleExists:      "Module already exists",
	ErrModuleInvalid:     "Invalid module data",
	ErrModuleCircular:    "Circular module reference detected",

	// PRD 相关错误
	ErrPRDNotFound:       "PRD not found",
	ErrPRDExists:         "PRD already exists",
	ErrPRDInvalid:        "Invalid PRD data",
	ErrPRDVersionInvalid: "Invalid PRD version",

	// 测试用例相关错误
	ErrTestCaseNotFound:  "Test case not found",
	ErrTestCaseExists:    "Test case already exists",
	ErrTestCaseInvalid:   "Invalid test case data",
	ErrTestStepInvalid:   "Invalid test step data",

	// 标签相关错误
	ErrTagNotFound:       "Tag not found",
	ErrTagExists:         "Tag already exists",
	ErrTagInvalid:        "Invalid tag data",

	// 文件相关错误
	ErrFileUploadFailed:  "File upload failed",
	ErrFileNotFound:      "File not found",
	ErrFileInvalid:       "Invalid file",
	ErrFileTooLarge:      "File too large",

	// 向量数据库相关错误
	ErrVectorSyncFailed:  "Vector sync failed",
	ErrVectorSearchFailed: "Vector search failed",
	ErrVectorNotFound:    "Vector not found",
}

// GetErrorMessage 获取错误消息
func GetErrorMessage(code int) string {
	if msg, ok := ErrorMessages[code]; ok {
		return msg
	}
	return "Unknown error"
}
