package router

import (
	"rag-backend/internal/api/handler"
	"rag-backend/internal/api/middleware"
	"rag-backend/internal/repository/postgres"
	moduleService "rag-backend/internal/service/module"
	prdService "rag-backend/internal/service/prd"
	projectService "rag-backend/internal/service/project"
	tagService "rag-backend/internal/service/tag"
	testcaseService "rag-backend/internal/service/testcase"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

// SetupRouter 设置路由
func SetupRouter(router *gin.Engine, db *gorm.DB) {
	// 创建仓储
	projectRepo := postgres.NewProjectRepository(db)
	moduleRepo := postgres.NewModuleRepository(db)
	tagRepo := postgres.NewTagRepository(db)
	prdRepo := postgres.NewPRDRepository(db)
	prdVersionRepo := postgres.NewPRDVersionRepository(db)
	testCaseRepo := postgres.NewTestCaseRepository(db)
	testStepRepo := postgres.NewTestStepRepository(db)

	// 创建服务
	projectSvc := projectService.NewService(projectRepo)
	moduleSvc := moduleService.NewService(moduleRepo)
	tagSvc := tagService.NewService(tagRepo)
	prdSvc := prdService.NewService(prdRepo, prdVersionRepo)
	testCaseSvc := testcaseService.NewService(testCaseRepo, testStepRepo)

	// 创建处理器
	projectHandler := handler.NewProjectHandler(projectSvc)
	moduleHandler := handler.NewModuleHandler(moduleSvc)
	tagHandler := handler.NewTagHandler(tagSvc)
	prdHandler := handler.NewPRDHandler(prdSvc)
	testCaseHandler := handler.NewTestCaseHandler(testCaseSvc)

	// API v1 路由组
	v1 := router.Group("/api/v1")
	{
		// 项目管理路由（不带参数的路由）
		projects := v1.Group("/projects")
		{
			projects.POST("", projectHandler.CreateProject)
			projects.GET("", projectHandler.ListProjects)
		}

		// 项目管理路由（带 ID 参数的路由）
		projectWithID := v1.Group("/projects/:id")
		{
			projectWithID.GET("", projectHandler.GetProject)
			projectWithID.PUT("", projectHandler.UpdateProject)
			projectWithID.DELETE("", projectHandler.DeleteProject)
			projectWithID.GET("/statistics", projectHandler.GetProjectStatistics)
		}

		// 需要项目 ID 验证的路由（使用 :id 而不是 :project_id）
		projectRoutes := v1.Group("/projects/:id")
		projectRoutes.Use(middleware.ProjectIDValidator(db))
		{
			// 模块管理路由
			modules := projectRoutes.Group("/modules")
			{
				modules.GET("/tree", moduleHandler.GetModuleTree)
				modules.POST("", moduleHandler.CreateModule)
				modules.PUT("/:module_id", moduleHandler.UpdateModule)
				modules.DELETE("/:module_id", moduleHandler.DeleteModule)
				modules.PUT("/sort", moduleHandler.SortModules)
			}

			// 标签管理路由
			tags := projectRoutes.Group("/tags")
			{
				tags.GET("", tagHandler.GetTags)
				tags.POST("", tagHandler.CreateTag)
				tags.PUT("/:tag_id", tagHandler.UpdateTag)
				tags.DELETE("/:tag_id", tagHandler.DeleteTag)
				tags.GET("/:tag_id/usage", tagHandler.GetTagUsage)
			}

			// PRD 文档管理路由
			prds := projectRoutes.Group("/prds")
			{
				prds.GET("", prdHandler.ListPRDs)
				prds.POST("", prdHandler.CreatePRD)
				prds.GET("/:prd_id", prdHandler.GetPRD)
				prds.PUT("/:prd_id", prdHandler.UpdatePRD)
				prds.DELETE("/:prd_id", prdHandler.DeletePRD)
				
				// PRD 状态管理
				prds.PUT("/:prd_id/status", prdHandler.UpdatePRDStatus)
				prds.POST("/:prd_id/publish", prdHandler.PublishPRD)
				prds.POST("/:prd_id/archive", prdHandler.ArchivePRD)
				
				// PRD 版本管理
				prds.GET("/:prd_id/versions", prdHandler.GetPRDVersions)
				prds.GET("/:prd_id/versions/compare", prdHandler.ComparePRDVersions)
				prds.GET("/:prd_id/versions/:version", prdHandler.GetPRDVersion)
				
				// PRD 标签管理
				prds.POST("/:prd_id/tags", prdHandler.AddPRDTag)
				prds.DELETE("/:prd_id/tags/:tag_id", prdHandler.RemovePRDTag)
			}

			// 测试用例管理路由
			testcases := projectRoutes.Group("/testcases")
			{
				testcases.GET("", testCaseHandler.ListTestCases)
				testcases.POST("", testCaseHandler.CreateTestCase)
				testcases.POST("/batch-delete", testCaseHandler.BatchDeleteTestCases)
				testcases.GET("/:testcase_id", testCaseHandler.GetTestCase)
				testcases.PUT("/:testcase_id", testCaseHandler.UpdateTestCase)
				testcases.DELETE("/:testcase_id", testCaseHandler.DeleteTestCase)
				
				// 测试用例标签管理
				testcases.POST("/:testcase_id/tags", testCaseHandler.AddTestCaseTag)
				testcases.DELETE("/:testcase_id/tags/:tag_id", testCaseHandler.RemoveTestCaseTag)
			}
		}
	}
}
