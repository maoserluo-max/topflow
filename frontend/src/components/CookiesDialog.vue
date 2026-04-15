<template>
  <el-dialog
    v-model="visible"
    title="Cookies 管理"
    width="680px"
    :close-on-click-modal="false"
    @open="loadCookies"
  >
    <el-tabs v-model="activeTab">
      <el-tab-pane label="YouTube" name="youtube">
        <div class="cookies-guide">
          <p class="guide-title">如何获取 YouTube Cookies：</p>
          <ol class="guide-steps">
            <li>安装浏览器扩展 <strong>"Get cookies.txt LOCALLY"</strong>（Chrome/Edge）</li>
            <li>在浏览器中登录 <strong>youtube.com</strong></li>
            <li>点击扩展图标，选择 <strong>"Export" 导出</strong></li>
            <li>将导出的内容粘贴到下方文本框中</li>
          </ol>
          <p class="guide-tip">提示：Cookies 有效期有限，如抓取失败请重新导出更新。建议使用隐身窗口登录后导出，避免 Cookie 轮换失效。</p>
        </div>
        <el-input
          v-model="cookiesData.youtube"
          type="textarea"
          :rows="8"
          placeholder="粘贴 YouTube cookies.txt 内容..."
          class="cookies-textarea"
        />
        <div v-if="cookiesUpdated.youtube" class="updated-info">
          最后更新：{{ cookiesUpdated.youtube }}
        </div>
      </el-tab-pane>

      <el-tab-pane label="TikTok" name="tiktok">
        <div class="cookies-guide">
          <p class="guide-title">如何获取 TikTok Cookies：</p>
          <ol class="guide-steps">
            <li>安装浏览器扩展 <strong>"Get cookies.txt LOCALLY"</strong>（Chrome/Edge）</li>
            <li>在浏览器中登录 <strong>tiktok.com</strong></li>
            <li>点击扩展图标，选择 <strong>"Export" 导出</strong></li>
            <li>将导出的内容粘贴到下方文本框中</li>
          </ol>
        </div>
        <el-input
          v-model="cookiesData.tiktok"
          type="textarea"
          :rows="8"
          placeholder="粘贴 TikTok cookies.txt 内容..."
          class="cookies-textarea"
        />
        <div v-if="cookiesUpdated.tiktok" class="updated-info">
          最后更新：{{ cookiesUpdated.tiktok }}
        </div>
      </el-tab-pane>

      <el-tab-pane label="Instagram" name="ins">
        <div class="cookies-guide">
          <p class="guide-title">如何获取 Instagram Cookies：</p>
          <ol class="guide-steps">
            <li>安装浏览器扩展 <strong>"Get cookies.txt LOCALLY"</strong>（Chrome/Edge）</li>
            <li>在浏览器中登录 <strong>instagram.com</strong></li>
            <li>点击扩展图标，选择 <strong>"Export" 导出</strong></li>
            <li>将导出的内容粘贴到下方文本框中</li>
          </ol>
        </div>
        <el-input
          v-model="cookiesData.ins"
          type="textarea"
          :rows="8"
          placeholder="粘贴 Instagram cookies.txt 内容..."
          class="cookies-textarea"
        />
        <div v-if="cookiesUpdated.ins" class="updated-info">
          最后更新：{{ cookiesUpdated.ins }}
        </div>
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClear" type="danger" plain :disabled="!cookiesData[activeTab]">
          清除当前平台
        </el-button>
        <div class="footer-right">
          <el-button @click="visible = false">取消</el-button>
          <el-button type="primary" @click="handleSave" :loading="saving">
            保存
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

const visible = ref(false)
const activeTab = ref('youtube')
const saving = ref(false)

const cookiesData = reactive({
  youtube: '',
  tiktok: '',
  ins: ''
})

const cookiesUpdated = reactive({
  youtube: '',
  tiktok: '',
  ins: ''
})

function open() {
  visible.value = true
}

async function loadCookies() {
  try {
    const res = await api.get('/cookies')
    for (const item of res) {
      cookiesData[item.platform] = ''
      cookiesUpdated[item.platform] = ''
    }
    for (const item of res) {
      if (item.has_content) {
        const contentRes = await api.get(`/cookies/content/${item.platform}`)
        cookiesData[item.platform] = contentRes.content || ''
      }
      if (item.updated_at) {
        cookiesUpdated[item.platform] = new Date(item.updated_at).toLocaleString('zh-CN')
      }
    }
  } catch (error) {
    console.error('Load cookies error:', error)
  }
}

async function handleSave() {
  saving.value = true
  try {
    const platform = activeTab.value
    const content = cookiesData[platform]
    await api.post('/cookies', { platform, content })
    ElMessage.success(`${getPlatformName(platform)} Cookies 保存成功`)
    await loadCookies()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function handleClear() {
  const platform = activeTab.value
  try {
    await ElMessageBox.confirm(
      `确定要清除 ${getPlatformName(platform)} 的 Cookies 吗？`,
      '确认清除',
      { type: 'warning' }
    )
    await api.delete(`/cookies/${platform}`)
    cookiesData[platform] = ''
    cookiesUpdated[platform] = ''
    ElMessage.success('Cookies 已清除')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清除失败')
    }
  }
}

function getPlatformName(platform) {
  const names = { youtube: 'YouTube', tiktok: 'TikTok', ins: 'Instagram' }
  return names[platform] || platform
}

defineExpose({ open })
</script>

<style scoped>
.cookies-guide {
  margin-bottom: 16px;
  padding: 12px 16px;
  border-radius: 8px;
  background-color: var(--el-fill-color-light);
  border: 1px solid var(--el-border-color-lighter);
}

.guide-title {
  font-weight: 600;
  margin-bottom: 8px;
  font-size: 14px;
}

.guide-steps {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  line-height: 1.8;
  color: var(--el-text-color-regular);
}

.guide-tip {
  margin-top: 8px;
  font-size: 12px;
  color: var(--el-color-warning);
  line-height: 1.5;
}

.cookies-textarea {
  margin-bottom: 8px;
}

.cookies-textarea :deep(.el-textarea__inner) {
  font-family: 'Courier New', Courier, monospace;
  font-size: 12px;
}

.updated-info {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-right {
  display: flex;
  gap: 8px;
}
</style>
