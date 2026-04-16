<template>
  <div class="min-h-screen p-8 space-y-6">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <h1 class="text-4xl font-bold gradient-text">视频管理</h1>
        <div class="flex items-center gap-2 ml-4">
          <button
            v-for="p in userProjects"
            :key="p"
            @click="switchProject(p)"
            class="project-btn"
            :class="{ 'project-btn-active': currentProject === p }"
          >
            {{ p }}
          </button>
        </div>
      </div>
      <div class="flex items-center">
        <button @click="showCreateDialog" class="cyber-button flex items-center gap-2 text-sm font-medium">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          新增视频
        </button>
        <button v-if="isAdmin" @click="exportCSV" class="cyber-button flex items-center gap-2 text-sm font-medium ml-3" style="background: linear-gradient(to right, #059669, #047857);">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          导出CSV
        </button>
      </div>
    </div>

    <div class="glass-card p-6 animate-in">
      <div class="flex items-center gap-3 mb-5">
        <span class="w-1.5 h-5 rounded-full bg-gradient-to-b from-cyber-blue to-cyber-purple"></span>
        <h3 class="text-sm font-semibold dark:text-gray-300 text-gray-600 uppercase tracking-wider">筛选条件</h3>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-x-4 gap-y-3">
        <div class="space-y-1">
          <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">平台</label>
          <select
            v-model="filters.platform"
            class="filter-select"
          >
            <option value="" class="dark:bg-gray-900 bg-white">全部平台</option>
            <option value="tiktok" class="dark:bg-gray-900 bg-white">TikTok</option>
            <option value="ins" class="dark:bg-gray-900 bg-white">Instagram</option>
            <option value="youtube" class="dark:bg-gray-900 bg-white">YouTube</option>
          </select>
        </div>

        <div class="space-y-1">
          <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">地区</label>
          <select
            v-model="filters.region"
            class="filter-select"
          >
            <option value="" class="dark:bg-gray-900 bg-white">全部地区</option>
            <option v-for="r in regionOptions" :key="r.value" :value="r.value" class="dark:bg-gray-900 bg-white">{{ r.label }}</option>
          </select>
        </div>

        <div class="space-y-1">
          <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">达人</label>
          <input
            v-model="filters.influencer_name"
            type="text"
            placeholder="搜索达人..."
            class="filter-input"
          />
        </div>

        <div class="space-y-1">
          <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">负责人</label>
          <select
            v-model="filters.contact_person"
            class="filter-select"
          >
            <option value="" class="dark:bg-gray-900 bg-white">全部负责人</option>
            <option v-for="u in userList" :key="u.username" :value="u.username" class="dark:bg-gray-900 bg-white">{{ u.full_name || u.username }}</option>
          </select>
        </div>

        <div class="space-y-1">
          <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">状态</label>
          <select
            v-model="filters.status"
            class="filter-select"
          >
            <option value="" class="dark:bg-gray-900 bg-white">全部状态</option>
            <option v-for="s in statusOptions" :key="s.value" :value="s.value" class="dark:bg-gray-900 bg-white">{{ s.label }}</option>
          </select>
        </div>

        <div class="space-y-1">
          <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">发布日期</label>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="—"
            start-placeholder="开始"
            end-placeholder="结束"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            class="!w-full date-picker-override"
          />
        </div>
      </div>

      <div class="flex flex-wrap items-center justify-between gap-3 mt-4 pt-4 dark:border-t dark:border-white/5 border-t border-gray-200">
        <div class="flex flex-wrap gap-1.5">
          <button
            v-for="shortcut in dateShortcuts"
            :key="shortcut.label"
            @click="applyDateShortcut(shortcut)"
            class="shortcut-btn"
            :class="{ 'shortcut-btn-active': activeShortcut === shortcut.label }"
          >
            {{ shortcut.label }}
          </button>
        </div>
        <div class="flex gap-2">
          <button @click="resetFilters" class="reset-btn">
            重置
          </button>
          <button @click="fetchVideos" class="search-btn">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            搜索
          </button>
        </div>
      </div>
    </div>

    <div class="glass-card overflow-hidden animate-in" style="animation-delay: 100ms">
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="space-y-4 text-center">
          <div class="w-12 h-12 mx-auto border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin"></div>
          <p class="dark:text-gray-400 text-gray-500 text-sm">加载数据中...</p>
        </div>
      </div>

      <div v-else class="overflow-x-auto scrollbar-hide">
        <table ref="tableRef" class="resizable-table">
          <thead>
            <tr>
              <th v-for="col in columns" :key="col.key"
                :style="{ width: col.width + 'px', minWidth: col.minWidth + 'px' }"
                :class="{ 'cursor-pointer select-none hover:bg-white/5': col.sortable }"
                @click="col.sortable && toggleSort(col.key)"
              >
                <div class="th-content" :class="col.align === 'right' ? 'justify-end' : col.align === 'center' ? 'justify-center' : ''">
                  <span>{{ col.label }}</span>
                  <span v-if="col.sortable" class="sort-icons">
                    <svg class="sort-arrow" :class="{ 'sort-active': sortState.field === col.key && sortState.order === 'asc' }" viewBox="0 0 10 6"><path d="M5 0L10 6H0z" fill="currentColor"/></svg>
                    <svg class="sort-arrow" :class="{ 'sort-active': sortState.field === col.key && sortState.order === 'desc' }" viewBox="0 0 10 6"><path d="M5 6L0 0h10z" fill="currentColor"/></svg>
                  </span>
                </div>
                <div v-if="col.resizable !== false" class="col-resizer" @mousedown.stop="startResize($event, col)"></div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(video, index) in videos" :key="video.id" class="group animate-in" :style="{ animationDelay: `${index * 50}ms` }">
              <td>
                <button @click="showVideoDetail(video)" class="font-mono text-sm text-cyber-blue hover:text-cyber-purple hover:underline transition-colors cursor-pointer whitespace-nowrap">
                  {{ video.video_code || '-' }}
                </button>
              </td>
              <td>
                <span class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-semibold whitespace-nowrap dark:bg-primary-500/15 dark:text-primary-300 dark:border dark:border-primary-500/25 bg-primary-50 text-primary-600 border border-primary-200">
                  {{ video.project || '-' }}
                </span>
              </td>
              <td class="text-sm dark:text-gray-300 text-gray-700 whitespace-nowrap">{{ video.content_direction || '-' }}</td>
              <td class="text-right font-mono text-cyber-green font-semibold whitespace-nowrap">${{ video.price_usd || '0' }}</td>
              <td class="text-sm dark:text-gray-300 text-gray-700 whitespace-nowrap">{{ video.contact_person || '-' }}</td>
              <td>
                <span class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium whitespace-nowrap" :class="getStatusClass(video.status)">
                  {{ getStatusName(video.status) }}
                </span>
              </td>
              <td class="font-mono text-xs dark:text-gray-400 text-gray-500 whitespace-nowrap">{{ getRegionName(video.region) }}</td>
              <td>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-semibold tracking-wide whitespace-nowrap" :class="getPlatformClass(video.platform)">
                  {{ video.platform?.toUpperCase() }}
                </span>
              </td>
              <td class="font-medium dark:text-white text-gray-900 whitespace-nowrap">{{ video.influencer_name }}</td>
              <td class="text-sm dark:text-gray-300 text-gray-700 whitespace-nowrap">{{ video.contact_email || '-' }}</td>
              <td class="text-sm dark:text-gray-300 text-gray-700 whitespace-nowrap">{{ video.contact_whatsapp || '-' }}</td>
              <td class="whitespace-nowrap">{{ video.title || '-' }}</td>
              <td class="text-sm text-gray-500 whitespace-nowrap">{{ formatDate(video.publish_date) }}</td>
              <td class="text-right font-mono text-cyber-blue whitespace-nowrap">{{ formatNumber(video.play_count) }}</td>
              <td class="text-right font-mono text-pink-400 whitespace-nowrap">{{ formatNumber(video.like_count) }}</td>
              <td class="text-right font-mono text-amber-400 whitespace-nowrap">{{ formatNumber(video.comment_count) }}</td>
              <td class="text-right font-mono text-emerald-400 whitespace-nowrap">{{ formatNumber(video.share_count) }}</td>
              <td class="text-right font-mono text-orange-400 font-semibold whitespace-nowrap">${{ calcCPM(video) }}</td>
              <td class="whitespace-nowrap">
                <button
                  v-if="video.video_url"
                  @click="openVideo(video.video_url)"
                  class="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium dark:bg-cyber-purple/10 dark:text-cyber-purple dark:hover:bg-cyber-purple/20 bg-purple-50 text-purple-600 hover:bg-purple-100 transition-colors"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  查看
                </button>
                <span v-else class="text-xs dark:text-gray-600 text-gray-400">-</span>
              </td>
              <td>
                <div class="flex items-center justify-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <button @click="editVideo(video)" class="p-1.5 rounded-lg hover:bg-cyber-blue/10 text-cyber-blue transition-colors" title="编辑">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                  </button>
                  <button @click="deleteVideo(video)" class="p-1.5 rounded-lg hover:bg-red-500/10 text-red-400 transition-colors" title="删除">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="videos.length === 0">
              <td :colspan="columns.length" class="text-center py-20">
                <div class="space-y-3">
                  <div class="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-primary-500/10 to-cyber-purple/10 flex items-center justify-center">
                    <svg class="w-10 h-10 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <p class="dark:text-gray-500 text-gray-500 text-sm">暂无视频数据</p>
                  <button @click="showCreateDialog" class="cyber-button text-sm px-4 py-2">添加第一条视频</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <Pagination
        v-model="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        show-page-size
        @change="fetchVideos"
      />
    </div>

    <VideoFormDialog
      ref="formDialogRef"
      :visible="dialogVisible"
      :is-edit="isEdit"
      :edit-data="editingVideo"
      :user-list="userList"
      @close="dialogVisible = false"
      @submitted="onDialogSubmitted"
    />

    <Teleport to="body">
      <Transition name="modal">
        <div v-if="detailVisible" class="fixed inset-0 z-50 overflow-y-auto" @click.self="detailVisible = false">
          <div class="sticky top-0 left-0 right-0 h-screen bg-black/60 backdrop-blur-sm transition-opacity" @click="detailVisible = false" />
          <div class="relative min-h-screen flex items-center justify-center p-4" style="margin-top: -100vh">
            <div class="relative w-full max-w-3xl glass-card p-8 animate-slide-up max-h-[90vh] overflow-y-auto scrollbar-hide" @click.stop>
              <button @click="detailVisible = false" class="absolute top-6 right-6 p-2 rounded-xl dark:hover:bg-white/10 dark:text-gray-400 dark:hover:text-white hover:bg-gray-100 text-gray-400 hover:text-gray-700 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
              </button>

              <div class="mb-6">
                <h2 class="text-2xl font-bold gradient-text mb-1">视频详情</h2>
                <p class="text-sm font-mono dark:text-cyber-blue text-primary-600">{{ detailData?.video_code || '-' }}</p>
              </div>

              <div class="space-y-6">
                <!-- 基本信息 -->
                <div>
                  <div class="flex items-center gap-3 mb-4">
                    <span class="w-1.5 h-5 rounded-full bg-gradient-to-b from-cyber-blue to-cyber-purple"></span>
                    <h3 class="text-sm font-semibold dark:text-gray-300 text-gray-600 uppercase tracking-wider">基本信息</h3>
                  </div>
                  <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div class="detail-field"><span class="detail-label">项目</span><span class="detail-value"><span class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-semibold dark:bg-primary-500/15 dark:text-primary-300 dark:border dark:border-primary-500/25 bg-primary-50 text-primary-600 border border-primary-200">{{ detailData?.project || '-' }}</span></span></div>
                    <div class="detail-field"><span class="detail-label">视频编号</span><span class="detail-value font-mono dark:text-cyber-blue text-primary-600">{{ detailData?.video_code || '-' }}</span></div>
                    <div class="detail-field"><span class="detail-label">内容方向</span><span class="detail-value">{{ detailData?.content_direction || '-' }}</span></div>
                    <div class="detail-field"><span class="detail-label">价格</span><span class="detail-value text-cyber-green font-semibold">${{ detailData?.price_usd || '0' }}</span></div>
                    <div class="detail-field"><span class="detail-label">负责人</span><span class="detail-value">{{ detailData?.contact_person || '-' }}</span></div>
                    <div class="detail-field"><span class="detail-label">状态</span><span class="detail-value"><span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium" :class="getStatusClass(detailData?.status)">{{ getStatusName(detailData?.status) }}</span></span></div>
                  </div>
                  <div v-if="detailData?.video_types" class="mt-4">
                    <span class="detail-label">视频类型</span>
                    <div class="flex flex-wrap gap-2 mt-1.5">
                      <span
                        v-for="t in detailData.video_types.split(',').map(s => s.trim()).filter(Boolean)"
                        :key="t"
                        class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium dark:bg-violet-500/10 dark:text-violet-400 dark:border dark:border-violet-500/25 bg-violet-50 text-violet-600 border border-violet-200"
                      >{{ t }}</span>
                    </div>
                  </div>
                </div>

                <!-- 属性信息 -->
                <div>
                  <div class="flex items-center gap-3 mb-4">
                    <span class="w-1.5 h-5 rounded-full bg-gradient-to-b from-amber-500 to-orange-500"></span>
                    <h3 class="text-sm font-semibold dark:text-gray-300 text-gray-600 uppercase tracking-wider">属性信息</h3>
                  </div>
                  <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div class="detail-field"><span class="detail-label">地区</span><span class="detail-value">{{ getRegionName(detailData?.region) }}</span></div>
                    <div class="detail-field"><span class="detail-label">平台</span><span class="detail-value">{{ detailData?.platform?.toUpperCase() || '-' }}</span></div>
                    <div class="detail-field"><span class="detail-label">达人名称</span><span class="detail-value">{{ detailData?.influencer_name || '-' }}</span></div>
                    <div class="detail-field"><span class="detail-label">邮箱</span><span class="detail-value">{{ detailData?.contact_email || '-' }}</span></div>
                    <div class="detail-field"><span class="detail-label">WhatsApp</span><span class="detail-value">{{ detailData?.contact_whatsapp || '-' }}</span></div>
                  </div>
                </div>

                <!-- 内容信息 -->
                <div>
                  <div class="flex items-center gap-3 mb-4">
                    <span class="w-1.5 h-5 rounded-full bg-gradient-to-b from-cyber-green to-emerald-500"></span>
                    <h3 class="text-sm font-semibold dark:text-gray-300 text-gray-600 uppercase tracking-wider">内容信息</h3>
                  </div>
                  <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div class="detail-field col-span-2 md:col-span-3"><span class="detail-label">视频标题</span><span class="detail-value">{{ detailData?.title || '-' }}</span></div>
                    <div class="detail-field"><span class="detail-label">发布日期</span><span class="detail-value">{{ formatDate(detailData?.publish_date) }}</span></div>
                    <div class="detail-field"><span class="detail-label">播放量</span><span class="detail-value font-mono text-cyber-blue">{{ formatNumber(detailData?.play_count) }}</span></div>
                    <div class="detail-field"><span class="detail-label">点赞数</span><span class="detail-value font-mono text-pink-400">{{ formatNumber(detailData?.like_count) }}</span></div>
                    <div class="detail-field"><span class="detail-label">评论数</span><span class="detail-value font-mono text-amber-400">{{ formatNumber(detailData?.comment_count) }}</span></div>
                    <div class="detail-field"><span class="detail-label">分享数</span><span class="detail-value font-mono text-emerald-400">{{ formatNumber(detailData?.share_count) }}</span></div>
                    <div class="detail-field"><span class="detail-label">CPM</span><span class="detail-value font-mono text-orange-400 font-semibold">${{ calcCPM(detailData) }}</span></div>
                  </div>
                  <div class="mt-4">
                    <div class="detail-field col-span-2 md:col-span-3"><span class="detail-label">视频链接</span><a v-if="detailData?.video_url" :href="detailData.video_url" target="_blank" class="detail-value text-cyber-blue hover:underline break-all">{{ detailData.video_url }}</a><span v-else class="detail-value">-</span></div>
                  </div>
                </div>

                <div>
                  <div class="flex items-center gap-3 mb-4">
                    <span class="w-1.5 h-5 rounded-full bg-gradient-to-b from-gray-400 to-gray-500"></span>
                    <h3 class="text-sm font-semibold dark:text-gray-300 text-gray-600 uppercase tracking-wider">系统信息</h3>
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                    <div class="detail-field"><span class="detail-label">创建时间</span><span class="detail-value">{{ formatDateTime(detailData?.created_at) }}</span></div>
                    <div class="detail-field"><span class="detail-label">更新时间</span><span class="detail-value">{{ formatDateTime(detailData?.updated_at) }}</span></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'
import Pagination from '@/components/Pagination.vue'
import VideoFormDialog from '@/components/VideoFormDialog.vue'

const userStore = useUserStore()
const themeStore = useThemeStore()
const loading = ref(false)
const videos = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dateRange = ref([])
const activeShortcut = ref('')
const tableRef = ref(null)

const sortState = reactive({ field: 'publish_date', order: 'desc' })

const columns = reactive([
  { key: 'video_code', label: '视频编号', width: 130, minWidth: 100, sortable: false, align: 'left', resizable: false },
  { key: 'project', label: '项目', width: 85, minWidth: 65, sortable: false, align: 'center' },
  { key: 'content_direction', label: '内容方向', width: 110, minWidth: 80, sortable: false, align: 'left' },
  { key: 'price_usd', label: '价格($)', width: 85, minWidth: 65, sortable: true, align: 'right' },
  { key: 'contact_person', label: '负责人', width: 80, minWidth: 60, sortable: false, align: 'left' },
  { key: 'status', label: '状态', width: 80, minWidth: 65, sortable: false, align: 'center' },
  { key: 'region', label: '地区', width: 100, minWidth: 70, sortable: false, align: 'left' },
  { key: 'platform', label: '平台', width: 80, minWidth: 60, sortable: false, align: 'center' },
  { key: 'influencer_name', label: '达人', width: 110, minWidth: 80, sortable: false, align: 'left' },
  { key: 'contact_email', label: '邮箱', width: 150, minWidth: 100, sortable: false, align: 'left' },
  { key: 'contact_whatsapp', label: 'WhatsApp', width: 110, minWidth: 80, sortable: false, align: 'left' },
  { key: 'title', label: '标题', width: 180, minWidth: 100, sortable: false, align: 'left' },
  { key: 'publish_date', label: '发布日期', width: 100, minWidth: 80, sortable: true, align: 'left' },
  { key: 'play_count', label: '播放量', width: 90, minWidth: 65, sortable: true, align: 'right' },
  { key: 'like_count', label: '点赞数', width: 85, minWidth: 65, sortable: true, align: 'right' },
  { key: 'comment_count', label: '评论数', width: 85, minWidth: 65, sortable: true, align: 'right' },
  { key: 'share_count', label: '转发数', width: 85, minWidth: 65, sortable: true, align: 'right' },
  { key: 'cpm', label: 'CPM', width: 80, minWidth: 60, sortable: true, align: 'right' },
  { key: 'video_url', label: '查看视频', width: 80, minWidth: 65, sortable: false, align: 'center' },
  { key: 'actions', label: '操作', width: 75, minWidth: 60, sortable: false, align: 'center', resizable: false }
])

const filters = reactive({
  platform: '',
  region: '',
  influencer_name: '',
  contact_person: '',
  status: ''
})

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingVideo = ref(null)
const detailVisible = ref(false)
const detailData = ref(null)
const formDialogRef = ref(null)

const userRole = computed(() => userStore.user?.role || '')
const isAdmin = computed(() => ['super_admin', 'admin'].includes(userRole.value))
const canSelectAllUsers = computed(() => ['super_admin', 'admin', 'leader'].includes(userRole.value))
const userProjects = computed(() => userStore.userProjects)
const currentProject = ref('')

const userList = ref([])

const regionOptions = [
  { value: 'ID', label: '印尼 (ID)' },
  { value: 'MY', label: '马来西亚 (MY)' },
  { value: 'TH', label: '泰国 (TH)' },
  { value: 'TW', label: '台湾 (TW)' },
  { value: 'KR', label: '韩国 (KR)' },
  { value: 'JP', label: '日本 (JP)' }
]

const directionOptions = [
  'Free Fire',
  'Mobile Legends'
]

const statusOptions = [
  { value: 'pending_review', label: '待审核' },
  { value: 'pending_publish', label: '待发布' },
  { value: 'published', label: '已发布' },
  { value: 'completed', label: '已完成' }
]

const dateShortcuts = [
  { label: '本周', getValue: () => { const now = new Date(); const day = now.getDay() || 7; const mon = new Date(now); mon.setDate(now.getDate() - day + 1); return [fmt(mon), fmt(now)]; } },
  { label: '上周', getValue: () => { const now = new Date(); const day = now.getDay() || 7; const mon = new Date(now); mon.setDate(now.getDate() - day - 6); const sun = new Date(mon); sun.setDate(mon.getDate() + 6); return [fmt(mon), fmt(sun)]; } },
  { label: '本月', getValue: () => { const now = new Date(); const first = new Date(now.getFullYear(), now.getMonth(), 1); return [fmt(first), fmt(now)]; } },
  { label: '上月', getValue: () => { const now = new Date(); const first = new Date(now.getFullYear(), now.getMonth() - 1, 1); const last = new Date(now.getFullYear(), now.getMonth(), 0); return [fmt(first), fmt(last)]; } },
  { label: '本年', getValue: () => { const now = new Date(); const first = new Date(now.getFullYear(), 0, 1); return [fmt(first), fmt(now)]; } }
]

function fmt(d) { const y = d.getFullYear(), m = String(d.getMonth() + 1).padStart(2, '0'), day = String(d.getDate()).padStart(2, '0'); return `${y}-${m}-${day}` }

function calcCPM(video) {
  if (!video) return '0.00'
  const price = Number(video.price_usd) || 0
  const plays = Number(video.play_count) || 0
  if (plays === 0) return '0.00'
  return ((price / plays) * 1000).toFixed(2)
}

function toggleSort(field) {
  if (sortState.field === field) {
    sortState.order = sortState.order === 'desc' ? 'asc' : 'desc'
  } else {
    sortState.field = field
    sortState.order = 'desc'
  }
  fetchVideos()
}

function startResize(e, col) {
  const startX = e.pageX
  const startWidth = col.width
  const onMove = (ev) => {
    const diff = ev.pageX - startX
    col.width = Math.max(col.minWidth, startWidth + diff)
  }
  const onUp = () => {
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onUp)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}

onMounted(async () => {
  if (userProjects.value.length > 0) {
    currentProject.value = userProjects.value[0]
  }
  fetchVideos()
  if (canSelectAllUsers.value) await fetchUsers()
})

function switchProject(p) {
  currentProject.value = p
  currentPage.value = 1
  fetchVideos()
}

async function fetchVideos() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      sort_by: sortState.field,
      sort_order: sortState.order,
      project: currentProject.value || undefined,
      ...filters
    }
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const response = await api.get('/videos/', { params })
    videos.value = response.items || []
    total.value = response.total || 0
    // 将已有数据传给 VideoFormDialog 用于收集选项
    if (formDialogRef.value) {
      formDialogRef.value.collectOptionsFromVideos(videos.value)
    }
  } catch (error) {
    console.error('Fetch videos error:', error)
  } finally {
    loading.value = false
  }
}

async function fetchUsers() {
  try {
    const response = await api.get('/auth/users')
    userList.value = Array.isArray(response) ? response : (response.items || [])
  } catch (error) {
    console.warn('获取用户列表失败:', error.message)
    userList.value = []
  }
}

function applyDateShortcut(shortcut) {
  activeShortcut.value = shortcut.label
  dateRange.value = shortcut.getValue()
}

function resetFilters() {
  Object.assign(filters, { platform: '', region: '', influencer_name: '', contact_person: '', status: '' })
  dateRange.value = []
  activeShortcut.value = ''
  currentPage.value = 1
  fetchVideos()
}

function showCreateDialog() { isEdit.value = false; editingVideo.value = null; dialogVisible.value = true }
function editVideo(video) { isEdit.value = true; editingVideo.value = { ...video }; dialogVisible.value = true }
function showVideoDetail(video) { detailData.value = video; detailVisible.value = true }
function onDialogSubmitted() { fetchVideos() }

function deleteVideo(video) {
  ElMessageBox.confirm(`确定要删除视频"${video.title || video.influencer_name}"吗？`, '提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(async () => {
    try { await api.delete(`/videos/${video.id}`); ElMessage.success('删除成功'); fetchVideos() }
    catch (error) { console.error('Delete error:', error) }
  }).catch(() => {})
}

function openVideo(url) { window.open(url, '_blank') }

async function exportCSV() {
  try {
    const params = {}
    if (currentProject.value) params.project = currentProject.value
    if (filters.platform) params.platform = filters.platform
    if (filters.region) params.region = filters.region
    if (filters.influencer_name) params.influencer_name = filters.influencer_name
    if (filters.contact_person) params.contact_person = filters.contact_person
    if (filters.status) params.status = filters.status
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const response = await api.get('/videos/export', { params, responseType: 'blob' })
    const blob = response instanceof Blob ? response : new Blob([response], { type: 'text/csv;charset=utf-8;' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `videos_${new Date().toISOString().slice(0, 10)}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Export error:', error)
    ElMessage.error('导出失败')
  }
}

function formatNumber(num) {
  if (!num) return '0'
  if (num >= 10000) return (num / 10000).toFixed(1) + 'w'
  return num.toLocaleString()
}

function formatDate(dateStr) { return !dateStr ? '-' : new Date(dateStr).toLocaleDateString('zh-CN') }
function formatDateTime(dateStr) { return !dateStr ? '-' : new Date(dateStr).toLocaleString('zh-CN') }

function getRegionName(region) { const f = regionOptions.find(r => r.value === region); return f ? f.label : region || '-' }
function getDirectionName(direction) { return direction || '-' }

function getPlatformClass(platform) {
  const c = {
    tiktok: 'dark:bg-black/40 dark:text-gray-200 dark:border-white/20 bg-gray-100 text-gray-700 border border-gray-200',
    ins: 'dark:bg-pink-500/10 dark:text-pink-400 dark:border-pink-500/30 bg-pink-50 text-pink-600 border border-pink-200',
    youtube: 'dark:bg-red-500/10 dark:text-red-400 dark:border-red-500/30 bg-red-50 text-red-600 border border-red-200'
  }
  return c[platform] || 'dark:bg-gray-500/10 dark:text-gray-300 dark:border-gray-500/30 bg-gray-100 text-gray-600 border border-gray-200'
}

function getStatusClass(status) {
  const c = {
    pending_review: 'dark:bg-blue-500/10 dark:text-blue-400 dark:border-blue-500/30 bg-blue-50 text-blue-600 border border-blue-200',
    pending_publish: 'dark:bg-amber-500/10 dark:text-amber-400 dark:border-amber-500/30 bg-amber-50 text-amber-600 border border-amber-200',
    published: 'dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/30 bg-emerald-50 text-emerald-600 border border-emerald-200',
    completed: 'dark:bg-purple-500/10 dark:text-purple-400 dark:border-purple-500/30 bg-purple-50 text-purple-600 border border-purple-200'
  }
  return c[status] || 'dark:bg-gray-500/10 dark:text-gray-400 dark:border-gray-500/30 bg-gray-100 text-gray-600 border border-gray-200'
}

function getStatusName(status) {
  return { pending_review: '待审核', pending_publish: '待发布', published: '已发布', completed: '已完成' }[status] || status
}
</script>

<style scoped>
.project-btn {
  padding: 6px 18px;
  border-radius: 10px;
  font-size: 0.8125rem;
  font-weight: 500;
  transition: all 0.2s;
  white-space: nowrap;
}
.dark .project-btn {
  background: rgba(255,255,255,0.05);
  color: #9ca3af;
  border: 1px solid rgba(255,255,255,0.1);
}
.project-btn {
  background: #f3f4f6;
  color: #6b7280;
  border: 1px solid #e5e7eb;
}
.dark .project-btn:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
  border-color: rgba(255,255,255,0.2);
}
.project-btn:hover {
  background: #e5e7eb;
  color: #111827;
  border-color: #d1d5db;
}
.project-btn-active {
  background: linear-gradient(to right, #4f46e5, #4338ca) !important;
  color: #fff !important;
  border-color: transparent !important;
  box-shadow: 0 4px 14px rgba(79,70,229,0.25);
}

.filter-select,
.filter-input {
  width: 100%;
  height: 38px;
  padding: 0 14px;
  border-radius: 10px;
  font-size: 0.8125rem;
  transition: all 0.2s;
}
.filter-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%239ca3af' viewBox='0 0 16 16'%3E%3Cpath d='M8 11L3 6h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 32px;
}
.dark .filter-select,
.dark .filter-input {
  background-color: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: #d1d5db;
}
.filter-select,
.filter-input {
  background-color: #fff;
  border: 1px solid #e5e7eb;
  color: #374151;
}
.filter-select:focus,
.filter-input:focus {
  border-color: rgba(59,130,246,0.5);
  outline: none;
  box-shadow: 0 0 0 3px rgba(59,130,246,0.15);
}
.dark .filter-select:focus,
.dark .filter-input:focus {
  border-color: rgba(59,130,246,0.5);
  box-shadow: 0 0 0 3px rgba(59,130,246,0.15);
}
.filter-input::placeholder {
  color: #9ca3af;
}
.dark .filter-input::placeholder {
  color: #4b5563;
}

.date-picker-override {
  height: 38px !important;
}
.date-picker-override :deep(.el-range-editor) {
  height: 38px !important;
  border-radius: 10px !important;
}
.date-picker-override :deep(.el-input__wrapper) {
  border-radius: 10px !important;
  height: 38px !important;
  box-shadow: none !important;
}
.dark .date-picker-override :deep(.el-input__wrapper) {
  background-color: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  box-shadow: none !important;
}
.date-picker-override :deep(.el-input__wrapper) {
  background-color: #fff !important;
  border: 1px solid #e5e7eb !important;
}

.shortcut-btn {
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 500;
  transition: all 0.2s;
}
.dark .shortcut-btn {
  background: rgba(255,255,255,0.05);
  color: #9ca3af;
}
.shortcut-btn {
  background: #f3f4f6;
  color: #6b7280;
}
.dark .shortcut-btn:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
}
.shortcut-btn:hover {
  background: #e5e7eb;
  color: #111827;
}
.shortcut-btn-active {
  background: rgba(59,130,246,0.15) !important;
  color: #3b82f6 !important;
}
.dark .shortcut-btn-active {
  background: rgba(59,130,246,0.2) !important;
  color: #60a5fa !important;
}

.reset-btn {
  padding: 6px 16px;
  border-radius: 10px;
  font-size: 0.8125rem;
  font-weight: 500;
  transition: all 0.2s;
}
.dark .reset-btn {
  color: #9ca3af;
  border: 1px solid rgba(255,255,255,0.1);
}
.reset-btn {
  color: #6b7280;
  border: 1px solid #e5e7eb;
  background: #fff;
}
.dark .reset-btn:hover {
  color: #fff;
  background: rgba(255,255,255,0.05);
}
.reset-btn:hover {
  color: #111827;
  background: #f3f4f6;
}

.search-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 20px;
  border-radius: 10px;
  font-size: 0.8125rem;
  font-weight: 500;
  background: linear-gradient(to right, #4f46e5, #4338ca);
  color: #fff;
  box-shadow: 0 4px 14px rgba(79,70,229,0.25);
  transition: all 0.2s;
}
.search-btn:hover {
  background: linear-gradient(to right, #6366f1, #4f46e5);
  box-shadow: 0 4px 14px rgba(79,70,229,0.4);
}

.resizable-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}
.resizable-table thead {
  position: sticky;
  top: 0;
  z-index: 10;
}
.resizable-table th {
  position: relative;
  padding: 12px 10px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
  user-select: none;
}
.dark .resizable-table th {
  color: #9ca3af;
  background: rgba(3,7,18,0.95);
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.resizable-table th {
  color: #6b7280;
  background: rgba(255,255,255,0.98);
  border-bottom: 1px solid #e5e7eb;
}

.th-content {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.sort-icons {
  display: inline-flex;
  flex-direction: column;
  gap: 1px;
  margin-left: 2px;
}
.sort-arrow {
  width: 8px;
  height: 5px;
  color: #d1d5db;
}
.dark .sort-arrow {
  color: rgba(255,255,255,0.15);
}
.sort-active {
  color: #3b82f6 !important;
}
.dark .sort-active {
  color: #60a5fa !important;
}

.col-resizer {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  cursor: col-resize;
  z-index: 5;
}
.col-resizer:hover,
.col-resizer:active {
  background: rgba(59,130,246,0.3);
}

.resizable-table td {
  padding: 10px;
  font-size: 0.8125rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.dark .resizable-table td {
  color: #d1d5db;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.resizable-table td {
  color: #374151;
  border-bottom: 1px solid #f3f4f6;
}
.resizable-table tbody tr {
  transition: background 0.15s;
}
.dark .resizable-table tbody tr:hover {
  background: rgba(255,255,255,0.03);
}
.resizable-table tbody tr:hover {
  background: #f9fafb;
}

.detail-field { display: flex; flex-direction: column; gap: 0.25rem; }
.detail-label { font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.dark .detail-label { color: #6b7280; }
.light .detail-label { color: #9ca3af; }
.detail-value { font-size: 0.875rem; font-weight: 500; }
.dark .detail-value { color: #e5e7eb; }
.light .detail-value { color: #111827; }
</style>
