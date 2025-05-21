<template>
  <div class="app-container">
    <el-container>
      <el-header>
        <h1>中文新闻信息检索系统</h1>
      </el-header>
      
      <el-main>
        <!-- 搜索区域 -->
        <div class="search-container">
          <el-input
            v-model="searchQuery"
            placeholder="请输入搜索关键词"
            class="search-input"
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button @click="handleSearch">
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
            </template>
          </el-input>
        </div>

        <!-- 搜索结果 -->
        <div class="results-container" v-if="searchResults.length > 0">
          <el-card v-for="(result, index) in searchResults" 
                  :key="index" 
                  class="result-card"
                  shadow="hover">
            <template #header>
              <div class="result-header">
                <h3>{{ result.title }}</h3>
                <el-tag size="small" type="info">{{ result.date }}</el-tag>
              </div>
            </template>
            <div class="result-content">
              <p>相关度：{{ (result.score * 100).toFixed(2) }}%</p>
              <p v-if="result.content" style="max-height: 3em; overflow: hidden; color: #888; font-size: 13px;">{{ result.content.slice(0, 80) }}{{ result.content.length > 80 ? '...' : '' }}</p>
              <el-button type="primary" link @click="openUrl(result.url)">
                查看原文
              </el-button>
              <el-button type="success" link @click="markRelevant(result)">
                标记相关
              </el-button>
              <el-button type="danger" link @click="markIrrelevant(result)">
                标记不相关
              </el-button>
              <el-button type="info" link @click="handleExtractInfo(result, index)">
                信息抽取
              </el-button>
            </div>
          </el-card>
        </div>

        <!-- 无结果提示 -->
        <el-empty v-else-if="hasSearched" description="未找到相关结果" />

        <!-- 系统统计信息 -->
        <el-card class="stats-card" v-if="stats">
          <template #header>
            <div class="stats-header">
              <h3>系统统计</h3>
            </div>
          </template>
          <div class="stats-content">
            <p>文档总数：{{ stats.doc_count }}</p>
            <p>词条总数：{{ stats.term_count }}</p>
            <p>平均文档长度：{{ stats.avg_doc_length.toFixed(2) }}</p>
          </div>
        </el-card>

        <!-- 信息抽取弹窗 -->
        <el-dialog v-model="extractDialogVisible" title="信息抽取结果" width="500px" :before-close="() => {extractDialogVisible = false}">
          <div v-if="extractInfo">
            <div v-for="(val, key) in extractInfo" :key="key" style="margin-bottom: 10px;">
              <strong>{{ key }}：</strong>
              <span v-if="Array.isArray(val)">{{ val.join('，') || '无' }}</span>
              <span v-else>{{ val || '无' }}</span>
            </div>
          </div>
          <div v-else>正在抽取信息...</div>
        </el-dialog>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage, ElDialog } from 'element-plus'

interface SearchResult {
  title: string
  date: string
  score: number
  url: string
  content?: string
}

interface SystemStats {
  doc_count: number
  term_count: number
  avg_doc_length: number
}

const searchQuery = ref('')
const searchResults = ref<SearchResult[]>([])
const hasSearched = ref(false)
const stats = ref<SystemStats | null>(null)

// 信息抽取相关
const extractDialogVisible = ref(false)
const extractInfo = ref<any>(null)
const extractingIndex = ref<number|null>(null)

// 获取系统统计信息
const fetchStats = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/stats')
    if (response.data.status === 'success') {
      stats.value = response.data.stats
    }
  } catch (error) {
    console.error('获取统计信息失败:', error)
  }
}

// 搜索处理
const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }

  try {
    const response = await axios.post('http://localhost:5000/api/search', {
      query: searchQuery.value,
      top_k: 10
    })

    if (response.data.status === 'success') {
      searchResults.value = response.data.results
      hasSearched.value = true
    }
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败，请稍后重试')
  }
}

// 打开原文链接
const openUrl = (url: string) => {
  window.open(url, '_blank')
}

// 标记相关
const markRelevant = async (result: any) => {
  try {
    await axios.post('http://localhost:5000/api/evaluate', {
      query: searchQuery.value,
      doc_url: result.url,
      is_relevant: true
    })
    ElMessage.success('已标记为相关')
  } catch (error) {
    console.error('标记失败:', error)
    ElMessage.error('标记失败，请稍后重试')
  }
}

// 标记不相关
const markIrrelevant = async (result: any) => {
  try {
    await axios.post('http://localhost:5000/api/evaluate', {
      query: searchQuery.value,
      doc_url: result.url,
      is_relevant: false
    })
    ElMessage.success('已标记为不相关')
  } catch (error) {
    console.error('标记失败:', error)
    ElMessage.error('标记失败，请稍后重试')
  }
}

// 信息抽取
const handleExtractInfo = async (result: any, idx: number) => {
  extractingIndex.value = idx
  extractInfo.value = null
  try {
    // 传递正文内容
    const response = await axios.post('http://localhost:5000/api/extract_info', {
      text: result.content // 传递正文内容
    })
    if (response.data.status === 'success') {
      extractInfo.value = response.data.info
      extractDialogVisible.value = true
    } else {
      ElMessage.error('信息抽取失败')
    }
  } catch (error) {
    ElMessage.error('信息抽取失败')
  }
}

// 组件挂载时获取统计信息
onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.el-header {
  text-align: center;
  padding: 20px 0;
}

.el-header h1 {
  margin: 0;
  color: #409EFF;
}

.search-container {
  max-width: 800px;
  margin: 20px auto;
}

.search-input {
  width: 100%;
}

.results-container {
  margin-top: 30px;
}

.result-card {
  margin-bottom: 20px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-header h3 {
  margin: 0;
  color: #303133;
}

.result-content {
  display: flex;
  gap: 10px;
  align-items: center;
}

.stats-card {
  margin-top: 30px;
}

.stats-header h3 {
  margin: 0;
  color: #303133;
}

.stats-content {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  text-align: center;
}

.stats-content p {
  margin: 0;
  font-size: 16px;
  color: #606266;
}
</style>
