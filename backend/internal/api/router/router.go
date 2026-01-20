package router

import (
	"rag-backend/internal/api/handler"
	"rag-backend/internal/api/middleware"
	"rag-backend/internal/repository/postgres"
	moduleService "rag-backend/internal/service/module"
	projectService "rag-backend/internal/service/project"
	tagService "rag-backend/internal/service/tag"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

// SetupRouter 设置路由
func SetupRouter(router *gin.Engine, db *gorm.DB) {
	// 创建仓储
	projectRepo := postgres.NewProjectRepository(db)
	moduleRepo := postgres.NewModuleRepository(db)
	tagRepo := postgres.NewTagRepository(db)

	// 创建服务
	projectSvc := projectService.NewService(projectRepo)
	moduleSvc := moduleService.NewService(moduleRepo)
	tagSvc := tagService.NewService(tagRepo)

	// 创建处理器
	projectHandler := handler.NewProjectHandler(projectSvc)
	moduleHandler := handler.NewModuleHandler(moduleSvc)
	tagHandler := handler.NewTagHandler(tagSvc)

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
		}
	}
}
