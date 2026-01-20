package middleware

import (
	"net/http"

	"rag-backend/internal/pkg/logger"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"go.uber.org/zap"
	"gorm.io/gorm"
)

// ProjectIDValidator 验证项目 ID 是否存在
func ProjectIDValidator(db *gorm.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		projectID := c.Param("id")
		if projectID == "" {
			c.JSON(http.StatusBadRequest, gin.H{
				"code":    400,
				"message": "Project ID is required",
			})
			c.Abort()
			return
		}

		// 验证 UUID 格式
		if _, err := uuid.Parse(projectID); err != nil {
			logger.Warn("Invalid project ID format",
				zap.String("project_id", projectID),
				zap.Error(err),
			)
			c.JSON(http.StatusBadRequest, gin.H{
				"code":    400,
				"message": "Invalid project ID format",
			})
			c.Abort()
			return
		}

		// 验证项目是否存在
		var count int64
		if err := db.Table("projects").Where("id = ? AND deleted_at IS NULL", projectID).Count(&count).Error; err != nil {
			logger.Error("Failed to check project existence",
				zap.String("project_id", projectID),
				zap.Error(err),
			)
			c.JSON(http.StatusInternalServerError, gin.H{
				"code":    500,
				"message": "Failed to validate project",
			})
			c.Abort()
			return
		}

		if count == 0 {
			c.JSON(http.StatusNotFound, gin.H{
				"code":    404,
				"message": "Project not found",
			})
			c.Abort()
			return
		}

		// 将项目 ID 存储到上下文中
		c.Set("project_id", projectID)
		c.Next()
	}
}
