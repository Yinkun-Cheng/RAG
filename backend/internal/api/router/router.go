package router

import (
	"rag-backend/internal/api/handler"
	"rag-backend/internal/api/middleware"
	"rag-backend/internal/repository/postgres"
	projectService "rag-backend/internal/service/project"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

// SetupRouter 设置路由
func SetupRouter(router *gin.Engine, db *gorm.DB) {
	// 创建仓储
	projectRepo := postgres.NewProjectRepository(db)

	// 创建服务
	projectSvc := projectService.NewService(projectRepo)

	// 创建处理器
	projectHandler := handler.NewProjectHandler(projectSvc)

	// API v1 路由组
	v1 := router.Group("/api/v1")
	{
		// 项目管理路由
		projects := v1.Group("/projects")
		{
			projects.POST("", projectHandler.CreateProject)
			projects.GET("", projectHandler.ListProjects)
			projects.GET("/:id", projectHandler.GetProject)
			projects.PUT("/:id", projectHandler.UpdateProject)
			projects.DELETE("/:id", projectHandler.DeleteProject)
			projects.GET("/:id/statistics", projectHandler.GetProjectStatistics)
		}

		// 需要项目 ID 验证的路由
		projectRoutes := v1.Group("/projects/:project_id")
		projectRoutes.Use(middleware.ProjectIDValidator(db))
		{
			// 后续添加模块、PRD、测试用例等路由
		}
	}
}
