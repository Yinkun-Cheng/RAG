package handler

import (
	"net/http"
	"strconv"

	"rag-backend/internal/domain/common"
	statisticsService "rag-backend/internal/service/statistics"

	"github.com/gin-gonic/gin"
)

// StatisticsHandler 统计处理器
type StatisticsHandler struct {
	service statisticsService.Service
}

// NewStatisticsHandler 创建统计处理器实例
func NewStatisticsHandler(service statisticsService.Service) *StatisticsHandler {
	return &StatisticsHandler{service: service}
}

// GetProjectStatistics 获取项目统计信息
// @Summary 获取项目统计信息
// @Tags 统计
// @Produce json
// @Param id path string true "项目ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/statistics [get]
func (h *StatisticsHandler) GetProjectStatistics(c *gin.Context) {
	projectID := c.Param("id")

	stats, err := h.service.GetProjectStatistics(projectID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to get project statistics",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(stats))
}

// GetTrends 获取趋势分析
// @Summary 获取趋势分析
// @Tags 统计
// @Produce json
// @Param id path string true "项目ID"
// @Param days query int false "天数" default(30)
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/statistics/trends [get]
func (h *StatisticsHandler) GetTrends(c *gin.Context) {
	projectID := c.Param("id")
	days, _ := strconv.Atoi(c.DefaultQuery("days", "30"))

	trends, err := h.service.GetTrends(projectID, days)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to get trends",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(trends))
}

// GetCoverage 获取覆盖率统计
// @Summary 获取覆盖率统计
// @Tags 统计
// @Produce json
// @Param id path string true "项目ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/statistics/coverage [get]
func (h *StatisticsHandler) GetCoverage(c *gin.Context) {
	projectID := c.Param("id")

	coverage, err := h.service.GetCoverage(projectID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to get coverage",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(coverage))
}
