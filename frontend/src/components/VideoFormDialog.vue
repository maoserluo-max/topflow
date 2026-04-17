<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="fixed inset-0 z-50 overflow-y-auto" @click.self="$emit('close')">
        <div class="sticky top-0 left-0 right-0 h-screen bg-black/60 backdrop-blur-sm transition-opacity" @click="$emit('close')" />

        <div class="relative min-h-screen flex items-center justify-center p-4" style="margin-top: -100vh">
          <div class="relative w-full max-w-4xl glass-card p-8 animate-slide-up max-h-[90vh] overflow-y-auto scrollbar-hide" @click.stop>
            <button
              @click="$emit('close')"
              class="absolute top-6 right-6 p-2 rounded-xl dark:hover:bg-white/10 dark:text-gray-400 dark:hover:text-white hover:bg-gray-100 text-gray-400 hover:text-gray-700 transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <div class="mb-8">
              <h2 class="text-2xl font-bold gradient-text mb-2">
                {{ isEdit ? '编辑视频' : '新增视频' }}
              </h2>
              <p v-if="!isEdit" class="text-sm dark:text-gray-400 text-gray-500 flex items-center gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-cyber-blue animate-pulse"></span>
                可粘贴链接并点击「抓取数据」自动填充信息
              </p>
            </div>

            <form @submit.prevent="handleSubmit" class="space-y-8">
              <!-- 视频链接 -->
              <div class="space-y-4">
                <div class="flex items-center gap-3">
                  <span class="w-1.5 h-5 rounded-full bg-gradient-to-b from-cyber-blue to-cyber-purple"></span>
                  <h3 class="text-sm font-semibold dark:text-gray-300 text-gray-600 uppercase tracking-wider">视频链接（可选）</h3>
                </div>
                <div class="flex gap-3">
                  <input
                    v-model="form.video_url"
                    type="url"
                    placeholder="粘贴 TikTok / Instagram / YouTube 链接..."
                    class="flex-1 px-5 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                  />
                  <button
                    type="button"
                    @click="fetchMetadata"
                    :disabled="!form.video_url?.trim()"
                    class="px-6 py-3 rounded-xl font-medium bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2 whitespace-nowrap"
                  >
                    <svg v-if="!fetching" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ fetching ? '抓取中...' : '抓取数据' }}
                  </button>
                </div>
              </div>

              <!-- 基本信息 -->
              <div class="space-y-4">
                <div class="flex items-center gap-3">
                  <span class="w-1.5 h-5 rounded-full bg-gradient-to-b from-cyber-blue to-cyber-purple"></span>
                  <h3 class="text-sm font-semibold dark:text-gray-300 text-gray-600 uppercase tracking-wider">基本信息</h3>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div class="space-y-1.5">
                    <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">项目 *</label>
                    <select
                      v-model="form.project"
                      required
                      class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                    >
                      <option v-for="p in availableProjects" :key="p" :value="p" class="dark:bg-gray-900 bg-white">{{ p }}</option>
                    </select>
                  </div>
                  <div class="space-y-1.5">
                    <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">视频编号</label>
                    <div class="flex gap-2">
                      <input
                        v-model="form.video_code"
                        type="text"
                        :placeholder="isEdit ? '手动输入编号' : '根据地区/方向/日期自动生成'"
                        class="flex-1 px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all font-mono"
                      />
                      <button
                        v-if="!isEdit"
                        type="button"
                        @click="refreshVideoCode"
                        class="px-3 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-400 dark:hover:bg-white/10 dark:hover:text-white bg-white border border-gray-200 text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition-all"
                        title="重新生成编号"
                      >
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                      </button>
                    </div>
                    <p v-if="!isEdit && form.video_code" class="text-xs dark:text-gray-600 text-gray-400">可手动修改编号</p>
                  </div>
                  <div class="space-y-1.5">
                    <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">内容方向</label>
                    <div class="flex gap-2">
                      <select
                        v-model="contentDirectionSelect"
                        @change="onContentDirectionSelect"
                        class="flex-1 px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                      >
                        <option value="" class="dark:bg-gray-900 bg-white">选择方向</option>
                        <option v-for="d in directionOptions" :key="d" :value="d" class="dark:bg-gray-900 bg-white">{{ d }}</option>
                        <option value="__custom__" class="dark:bg-gray-900 bg-white">+ 自定义输入</option>
                      </select>
                    </div>
                    <input
                      v-if="contentDirectionSelect === '__custom__'"
                      v-model="form.content_direction"
                      type="text"
                      placeholder="输入自定义内容方向"
                      class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                    />
                    <!-- 管理员可管理内容方向选项 -->
                    <div v-if="isAdmin" class="flex flex-wrap gap-1.5 mt-1">
                      <span
                        v-for="d in allDirectionOptions"
                        :key="d"
                        class="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium dark:bg-white/5 dark:text-gray-300 bg-gray-50 text-gray-600 dark:border dark:border-white/10 border border-gray-200"
                        :class="{ 'opacity-50': defaultDirectionOptions.includes(d) }"
                      >
                        {{ d }}
                        <button
                          v-if="!defaultDirectionOptions.includes(d)"
                          @click="removeDirectionOption(d)"
                          type="button"
                          class="dark:text-red-400 text-red-500 hover:text-red-600 dark:hover:text-red-300 ml-0.5"
                          title="删除此选项"
                        >×</button>
                      </span>
                    </div>
                  </div>
                  <div class="space-y-1.5">
                    <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">价格 (USD)</label>
                    <input
                      v-model.number="form.price_usd"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                    />
                  </div>
                  <div class="space-y-1.5">
                    <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">负责人</label>
                    <select
                      v-if="canSelectAllUsers"
                      v-model="form.contact_person"
                      class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                    >
                      <option value="" class="dark:bg-gray-900 bg-white">选择负责人</option>
                      <option v-for="u in userList" :key="u.username" :value="u.username" class="dark:bg-gray-900 bg-white">{{ u.full_name || u.username }}</option>
                    </select>
                    <input
                      v-else
                      :value="currentUser"
                      disabled
                      class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 opacity-50 cursor-not-allowed"
                    />
                  </div>
                  <div class="space-y-1.5">
                    <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">状态</label>
                    <select
                      v-model="form.status"
                      class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                    >
                      <option v-for="s in statusOptions" :key="s.value" :value="s.value" class="dark:bg-gray-900 bg-white">{{ s.label }}</option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- 视频类型 -->
              <div class="space-y-4">
                <div class="flex items-center gap-3">
                  <span class="w-1.5 h-5 rounded-full bg-gradient-to-b from-violet-500 to-purple-500"></span>
                  <h3 class="text-sm font-semibold dark:text-gray-300 text-gray-600 uppercase tracking-wider">视频类型（可多选）</h3>
                </div>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="t in videoTypeOptions"
                    :key="t"
                    type="button"
                    @click="toggleVideoType(t)"
                    class="px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 border"
                    :class="selectedVideoTypes.includes(t)
                      ? 'dark:bg-violet-500/20 dark:text-violet-300 dark:border-violet-500/40 bg-violet-50 text-violet-600 border-violet-300 shadow-sm'
                      : 'dark:bg-white/5 dark:text-gray-400 dark:border-white/10 dark:hover:bg-white/10 dark:hover:text-gray-300 bg-white text-gray-500 border-gray-200 hover:bg-gray-50 hover:text-gray-700'"
                  >
                    <span v-if="selectedVideoTypes.includes(t)" class="mr-1">✓</span>
                    {{ t }}
                  </button>
                </div>
                <div class="flex gap-2 items-center">
                  <input
                    v-model="customVideoType"
                    type="text"
                    placeholder="输入自定义类型并回车添加"
                    class="flex-1 px-4 py-2.5 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-violet-500/50 focus:outline-none focus:ring-2 focus:ring-violet-500/20 transition-all text-sm"
                    @keydown.enter.prevent="addCustomVideoType"
                  />
                  <button
                    type="button"
                    @click="addCustomVideoType"
                    :disabled="!customVideoType.trim()"
                    class="px-4 py-2.5 rounded-xl text-sm font-medium dark:bg-violet-500/10 dark:text-violet-400 dark:hover:bg-violet-500/20 bg-violet-50 text-violet-600 hover:bg-violet-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    添加
                  </button>
                </div>
              </div>

              <!-- 属性信息 -->
              <div class="space-y-4">
                <div class="flex items-center gap-3">
                  <span class="w-1.5 h-5 rounded-full bg-gradient-to-b from-amber-500 to-orange-500"></span>
                  <h3 class="text-sm font-semibold dark:text-gray-300 text-gray-600 uppercase tracking-wider">属性信息</h3>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div class="space-y-1.5">
                    <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">地区</label>
                    <select
                      v-model="form.region"
                      class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 focus:border-amber-500/50 focus:outline-none focus:ring-2 focus:ring-amber-500/20 transition-all"
                    >
                      <option value="" class="dark:bg-gray-900 bg-white">选择地区</option>
                      <option v-for="r in regionOptions" :key="r.value" :value="r.value" class="dark:bg-gray-900 bg-white">{{ r.label }}</option>
                    </select>
                  </div>
                  <div class="space-y-1.5">
                    <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">平台 *</label>
                    <select
                      v-model="form.platform"
                      class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 focus:border-amber-500/50 focus:outline-none focus:ring-2 focus:ring-amber-500/20 transition-all"
                    >
                      <option value="tiktok" class="dark:bg-gray-900 bg-white">TikTok</option>
                      <option value="ins" class="dark:bg-gray-900 bg-white">Instagram</option>
                      <option value="youtube" class="dark:bg-gray-900 bg-white">YouTube</option>
                    </select>
                  </div>
                  <div class="space-y-1.5">
                    <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">达人名称 *</label>
                    <input
                      v-model="form.influencer_name"
                      type="text"
                      required
                      placeholder="输入达人名称"
                      class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-amber-500/50 focus:outline-none focus:ring-2 focus:ring-amber-500/20 transition-all"
                    />
                  </div>
                  <div class="space-y-1.5">
                    <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">邮箱</label>
                    <input v-model="form.contact_email" type="email" placeholder="联系邮箱地址" class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-amber-500/50 focus:outline-none focus:ring-2 focus:ring-amber-500/20 transition-all" />
                  </div>
                  <div class="space-y-1.5">
                    <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">WhatsApp</label>
                    <input v-model="form.contact_whatsapp" type="tel" placeholder="WhatsApp号码" class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-amber-500/50 focus:outline-none focus:ring-2 focus:ring-amber-500/20 transition-all" />
                  </div>
                </div>
              </div>

              <!-- 内容信息 -->
              <div class="space-y-4">
                <div class="flex items-center gap-3">
                  <span class="w-1.5 h-5 rounded-full bg-gradient-to-b from-cyber-green to-emerald-500"></span>
                  <h3 class="text-sm font-semibold dark:text-gray-300 text-gray-600 uppercase tracking-wider">内容信息</h3>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div class="space-y-1.5 md:col-span-2">
                    <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">视频标题</label>
                    <input
                      v-model="form.title"
                      type="text"
                      placeholder="视频标题（可选）"
                      class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-green/50 focus:outline-none focus:ring-2 focus:ring-cyber-green/20 transition-all"
                    />
                  </div>
                  <div class="space-y-1.5">
                    <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">发布日期</label>
                    <input
                      v-model="form.publish_date"
                      type="date"
                      class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 focus:border-cyber-green/50 focus:outline-none focus:ring-2 focus:ring-cyber-green/20 transition-all"
                    />
                  </div>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-4 gap-5">
                  <div class="space-y-1.5">
                    <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">播放量</label>
                    <input v-model.number="form.play_count" type="number" class="w-full px-4 py-2.5 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 focus:border-cyber-green/50 focus:outline-none focus:ring-2 focus:ring-cyber-green/20 transition-all" />
                  </div>
                  <div class="space-y-1.5">
                    <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">点赞数</label>
                    <input v-model.number="form.like_count" type="number" class="w-full px-4 py-2.5 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 focus:border-cyber-green/50 focus:outline-none focus:ring-2 focus:ring-cyber-green/20 transition-all" />
                  </div>
                  <div class="space-y-1.5">
                    <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">评论数</label>
                    <input v-model.number="form.comment_count" type="number" class="w-full px-4 py-2.5 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 focus:border-cyber-green/50 focus:outline-none focus:ring-2 focus:ring-cyber-green/20 transition-all" />
                  </div>
                  <div class="space-y-1.5">
                    <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">分享数</label>
                    <input v-model.number="form.share_count" type="number" class="w-full px-4 py-2.5 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 focus:border-cyber-green/50 focus:outline-none focus:ring-2 focus:ring-cyber-green/20 transition-all" />
                  </div>
                </div>
              </div>

              <div class="flex justify-end gap-4 pt-6 dark:border-t dark:border-white/5 border-t border-gray-200">
                <button
                  type="button"
                  @click="$emit('close')"
                  class="px-8 py-3 rounded-xl text-sm font-medium dark:text-gray-400 dark:hover:text-white dark:hover:bg-white/5 dark:border-white/10 dark:hover:border-white/20 text-gray-500 hover:text-gray-900 hover:bg-gray-100 border border-gray-200 hover:border-gray-300 transition-all duration-200"
                >
                  取消
                </button>
                <button
                  type="submit"
                  :disabled="submitting"
                  class="px-8 py-3 rounded-xl text-sm font-medium bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-500 hover:to-primary-600 text-white shadow-lg shadow-primary-500/25 hover:shadow-primary-500/40 disabled:opacity-70 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2"
                >
                  <svg v-if="submitting" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ submitting ? '提交中...' : (isEdit ? '保存修改' : '创建视频') }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const props = defineProps({
  visible: Boolean,
  isEdit: Boolean,
  editData: { type: Object, default: null },
  userList: { type: Array, default: () => [] }
})

const emit = defineEmits(['close', 'submitted'])

const userStore = useUserStore()
const submitting = ref(false)
const fetching = ref(false)

const currentUser = computed(() => userStore.user?.username || '')
const userRole = computed(() => userStore.user?.role || '')
const canSelectAllUsers = computed(() => ['admin', 'leader'].includes(userRole.value))
const availableProjects = computed(() => userStore.userProjects)

const regionOptions = [
  { value: 'ID', label: '印尼 (ID)' },
  { value: 'MY', label: '马来西亚 (MY)' },
  { value: 'TH', label: '泰国 (TH)' },
  { value: 'TW', label: '台湾 (TW)' },
  { value: 'KR', label: '韩国 (KR)' },
  { value: 'JP', label: '日本 (JP)' }
]

const defaultDirectionOptions = ['FF', 'MLBB']

// 视频类型预设选项
const defaultVideoTypeOptions = ['高光混剪', '游戏解说', '纯画面展示', '特效/卡点', '真人', '剧情', '整蛊']

// 动态收集所有出现过的内容方向和视频类型
const allDirectionOptions = ref([...defaultDirectionOptions])
const allVideoTypeOptions = ref([...defaultVideoTypeOptions])

const directionOptions = computed(() => allDirectionOptions.value)
const videoTypeOptions = computed(() => allVideoTypeOptions.value)

const isAdmin = computed(() => userStore.user?.role === 'admin')

function removeDirectionOption(option) {
  allDirectionOptions.value = allDirectionOptions.value.filter(d => d !== option)
  // 如果当前选中的是被删除的选项，重置选择
  if (contentDirectionSelect.value === option) {
    contentDirectionSelect.value = ''
    form.content_direction = ''
  }
}

const statusOptions = [
  { value: 'pending_review', label: '待审核' },
  { value: 'pending_publish', label: '待发布' },
  { value: 'published', label: '已发布' },
  { value: 'completed', label: '已完成' }
]

const defaultForm = {
  video_code: '',
  project: '',
  platform: 'tiktok',
  region: '',
  content_direction: '',
  video_types: '',
  influencer_name: '',
  price_usd: null,
  title: '',
  publish_date: new Date().toISOString().split('T')[0],
  play_count: 0,
  like_count: 0,
  comment_count: 0,
  share_count: 0,
  video_url: '',
  contact_person: '',
  contact_email: '',
  contact_whatsapp: '',
  status: 'pending_review'
}

const form = reactive({ ...defaultForm })

// 视频类型多选
const selectedVideoTypes = ref([])
const customVideoType = ref('')

// 内容方向选择
const contentDirectionSelect = ref('')

function onContentDirectionSelect() {
  if (contentDirectionSelect.value === '__custom__') {
    form.content_direction = ''
  } else {
    form.content_direction = contentDirectionSelect.value
  }
}

function toggleVideoType(type) {
  const idx = selectedVideoTypes.value.indexOf(type)
  if (idx >= 0) {
    selectedVideoTypes.value.splice(idx, 1)
  } else {
    selectedVideoTypes.value.push(type)
  }
  form.video_types = selectedVideoTypes.value.join(',')
}

function addCustomVideoType() {
  const val = customVideoType.value.trim()
  if (!val) return
  if (!allVideoTypeOptions.value.includes(val)) {
    allVideoTypeOptions.value.push(val)
  }
  if (!selectedVideoTypes.value.includes(val)) {
    selectedVideoTypes.value.push(val)
    form.video_types = selectedVideoTypes.value.join(',')
  }
  customVideoType.value = ''
}

// 从已有视频数据中收集所有出现过的选项
function collectOptionsFromVideos(videos) {
  if (!videos) return
  const directions = new Set(allDirectionOptions.value)
  const types = new Set(allVideoTypeOptions.value)
  for (const v of videos) {
    if (v.content_direction && !defaultDirectionOptions.includes(v.content_direction)) {
      directions.add(v.content_direction)
    }
    if (v.video_types) {
      for (const t of v.video_types.split(',')) {
        const trimmed = t.trim()
        if (trimmed && !defaultVideoTypeOptions.includes(trimmed)) {
          types.add(trimmed)
        }
      }
    }
  }
  allDirectionOptions.value = [...directions]
  allVideoTypeOptions.value = [...types]
}

watch(() => props.visible, (val) => {
  if (val) {
    if (props.isEdit && props.editData) {
      Object.assign(form, {
        video_code: props.editData.video_code || '',
        project: props.editData.project || availableProjects.value[0] || 'Gamoji',
        platform: props.editData.platform,
        region: props.editData.region,
        content_direction: props.editData.content_direction,
        video_types: props.editData.video_types || '',
        influencer_name: props.editData.influencer_name,
        price_usd: props.editData.price_usd,
        title: props.editData.title,
        publish_date: props.editData.publish_date ? props.editData.publish_date.split('T')[0] : new Date().toISOString().split('T')[0],
        play_count: props.editData.play_count,
        like_count: props.editData.like_count,
        comment_count: props.editData.comment_count,
        share_count: props.editData.share_count,
        video_url: props.editData.video_url,
        contact_person: props.editData.contact_person,
        contact_email: props.editData.contact_email,
        contact_whatsapp: props.editData.contact_whatsapp,
        status: props.editData.status
      })
      // 解析 video_types 到 selectedVideoTypes
      selectedVideoTypes.value = form.video_types ? form.video_types.split(',').map(s => s.trim()).filter(Boolean) : []
      // 设置 contentDirectionSelect
      if (form.content_direction && allDirectionOptions.value.includes(form.content_direction)) {
        contentDirectionSelect.value = form.content_direction
      } else if (form.content_direction) {
        // 已有的自定义值，加入选项
        allDirectionOptions.value.push(form.content_direction)
        contentDirectionSelect.value = form.content_direction
      } else {
        contentDirectionSelect.value = ''
      }
      // 收集已有视频类型
      if (form.video_types) {
        for (const t of selectedVideoTypes.value) {
          if (!allVideoTypeOptions.value.includes(t)) {
            allVideoTypeOptions.value.push(t)
          }
        }
      }
    } else {
      codeManuallyEdited = false
      Object.assign(form, {
        ...defaultForm,
        project: availableProjects.value[0] || 'Gamoji',
        publish_date: new Date().toISOString().split('T')[0],
        contact_person: canSelectAllUsers.value ? '' : currentUser.value
      })
      selectedVideoTypes.value = []
      contentDirectionSelect.value = ''
    }
  }
})

async function handleSubmit() {
  submitting.value = true
  try {
    const data = { ...form }
    if (props.isEdit) {
      await api.put(`/videos/${props.editData.id}`, data)
      ElMessage.success('更新成功')
    } else {
      await api.post('/videos/', data)
      ElMessage.success('创建成功')
    }
    emit('submitted')
    emit('close')
  } catch (error) {
    const detail = error?.response?.data?.detail
    if (detail) {
      ElMessage.warning(detail)
    } else {
      ElMessage.error('操作失败')
    }
    console.error('Submit error:', error)
  } finally {
    submitting.value = false
  }
}

async function fetchMetadata() {
  if (!form.video_url?.trim()) {
    ElMessage.warning('请先输入视频链接')
    return
  }
  fetching.value = true
  try {
    const response = await api.post('/videos/fetch-metadata', { url: form.video_url })
    ElMessage.success('抓取成功！已自动填充表单')
    Object.assign(form, {
      platform: response.platform || form.platform,
      influencer_name: response.influencer_name || form.influencer_name,
      title: response.video_title || form.title,
      play_count: response.play_count || 0,
      like_count: response.like_count || 0,
      comment_count: response.comment_count || 0,
      share_count: response.share_count || 0
    })
    if (response.publish_date) {
      const raw = String(response.publish_date)
      if (/^\d{8}$/.test(raw)) {
        form.publish_date = `${raw.slice(0, 4)}-${raw.slice(4, 6)}-${raw.slice(6, 8)}`
      } else if (raw.length >= 10) {
        form.publish_date = raw.slice(0, 10)
      }
    }
  } catch (error) {
    console.error('Fetch metadata error:', error)
    const serverMsg = error?.response?.data?.detail
    if (serverMsg) {
      ElMessage.warning(serverMsg)
    } else {
      ElMessage.warning('抓取失败，请手动填写数据')
    }
  } finally {
    fetching.value = false
  }
}

let codeManuallyEdited = false

async function refreshVideoCode() {
  if (!form.region || !form.content_direction || !form.publish_date) {
    ElMessage.warning('请先选择地区、内容方向和发布日期')
    return
  }
  codeManuallyEdited = false
  try {
    const resp = await api.get('/videos/generate-code', {
      params: {
        region: form.region,
        content_direction: form.content_direction,
        publish_date: form.publish_date
      }
    })
    form.video_code = resp.video_code
  } catch (e) {
    console.error('Generate code error:', e)
  }
}

watch(() => form.video_code, (newVal, oldVal) => {
  if (oldVal === '' && newVal !== '') {
    codeManuallyEdited = true
  }
})

watch([() => form.region, () => form.content_direction, () => form.publish_date], async () => {
  if (props.isEdit || codeManuallyEdited) return
  if (!form.region || !form.content_direction || !form.publish_date) return
  try {
    const resp = await api.get('/videos/generate-code', {
      params: {
        region: form.region,
        content_direction: form.content_direction,
        publish_date: form.publish_date
      }
    })
    form.video_code = resp.video_code
  } catch (e) {
    console.error('Generate code error:', e)
  }
})

// 暴露收集方法给父组件
defineExpose({ collectOptionsFromVideos })
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .glass-card,
.modal-leave-active .glass-card {
  transition: all 0.3s ease;
}

.modal-enter-from .glass-card {
  transform: scale(0.95) translateY(20px);
  opacity: 0;
}

.modal-leave-to .glass-card {
  transform: scale(0.95) translateY(20px);
  opacity: 0;
}
</style>
