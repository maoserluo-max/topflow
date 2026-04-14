<template>
  <div class="min-h-screen p-8 space-y-8">
    <!-- 页面标题区 -->
    <div class="flex items-center justify-between">
      <div class="space-y-1">
        <h1 class="text-4xl font-bold gradient-text">视频管理</h1>
        <p :class="themeStore.isDark ? 'text-gray-400' : 'text-gray-500'" class="text-sm">管理所有达人视频数据，支持自动抓取元数据</p>
      </div>
      <button @click="showCreateDialog" class="cyber-button flex items-center gap-2 text-sm font-medium">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        新增视频
      </button>
    </div>

    <!-- 筛选栏 - 玻璃拟态 -->
    <div class="glass-card p-6 animate-in">
      <div class="flex items-center gap-3 mb-4">
        <span class="w-1.5 h-5 rounded-full bg-gradient-to-b from-cyber-blue to-cyber-purple"></span>
        <h3 :class="themeStore.isDark ? 'text-sm font-semibold text-gray-300 uppercase tracking-wider' : 'text-sm font-semibold text-gray-600 uppercase tracking-wider'">筛选条件</h3>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
        <!-- 平台 -->
        <div class="space-y-1.5">
          <label :class="themeStore.isDark ? 'text-xs text-gray-500 font-medium uppercase tracking-wide' : 'text-xs text-gray-600 font-medium uppercase tracking-wide'">平台</label>
          <select
            v-model="filters.platform"
            :class="themeStore.isDark
              ? 'w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all'
              : 'w-full px-4 py-2.5 rounded-xl bg-white border border-gray-200 text-gray-700 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all'"
          >
            <option value="" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">全部平台</option>
            <option value="tiktok" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">TikTok</option>
            <option value="ins" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">Instagram</option>
            <option value="youtube" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">YouTube</option>
          </select>
        </div>

        <!-- 地区 -->
        <div class="space-y-1.5">
          <label :class="themeStore.isDark ? 'text-xs text-gray-500 font-medium uppercase tracking-wide' : 'text-xs text-gray-600 font-medium uppercase tracking-wide'">地区</label>
          <select
            v-model="filters.region"
            :class="themeStore.isDark
              ? 'w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all'
              : 'w-full px-4 py-2.5 rounded-xl bg-white border border-gray-200 text-gray-700 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all'"
          >
            <option value="" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">全部地区</option>
            <option v-for="r in regionOptions" :key="r.value" :value="r.value" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">{{ r.label }}</option>
          </select>
        </div>

        <!-- 达人名称 -->
        <div class="space-y-1.5">
          <label :class="themeStore.isDark ? 'text-xs text-gray-500 font-medium uppercase tracking-wide' : 'text-xs text-gray-600 font-medium uppercase tracking-wide'">达人</label>
          <input
            v-model="filters.influencer_name"
            type="text"
            placeholder="搜索达人..."
            :class="themeStore.isDark
              ? 'w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 placeholder-gray-600 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all'
              : 'w-full px-4 py-2.5 rounded-xl bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all'"
          />
        </div>

        <!-- 状态 -->
        <div class="space-y-1.5">
          <label :class="themeStore.isDark ? 'text-xs text-gray-500 font-medium uppercase tracking-wide' : 'text-xs text-gray-600 font-medium uppercase tracking-wide'">状态</label>
          <select
            v-model="filters.status"
            :class="themeStore.isDark
              ? 'w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all'
              : 'w-full px-4 py-2.5 rounded-xl bg-white border border-gray-200 text-gray-700 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all'"
          >
            <option value="" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">全部状态</option>
            <option v-for="s in statusOptions" :key="s.value" :value="s.value" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">{{ s.label }}</option>
          </select>
        </div>

        <!-- 日期范围 -->
        <div class="space-y-1.5 lg:col-span-2">
          <label :class="themeStore.isDark ? 'text-xs text-gray-500 font-medium uppercase tracking-wide' : 'text-xs text-gray-600 font-medium uppercase tracking-wide'">发布日期</label>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            :class="themeStore.isDark ? '!w-full !bg-white/5 !border-white/10 !rounded-xl' : '!w-full !bg-white !border-gray-200 !rounded-xl'"
          />
        </div>
      </div>

      <!-- 操作按钮 -->
      <div :class="themeStore.isDark ? 'flex justify-end gap-3 mt-6 pt-4 border-t border-white/5' : 'flex justify-end gap-3 mt-6 pt-4 border-t border-gray-200'">
        <button
          @click="resetFilters"
          :class="themeStore.isDark
            ? 'px-5 py-2 rounded-xl text-sm font-medium text-gray-400 hover:text-white hover:bg-white/5 border border-white/10 hover:border-white/20 transition-all duration-200'
            : 'px-5 py-2 rounded-xl text-sm font-medium text-gray-500 hover:text-gray-900 hover:bg-gray-100 border border-gray-200 hover:border-gray-300 transition-all duration-200'"
        >
          重置筛选
        </button>
        <button
          @click="fetchVideos"
          class="px-6 py-2 rounded-xl text-sm font-medium bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-500 hover:to-primary-600 text-white shadow-lg shadow-primary-500/25 hover:shadow-primary-500/40 transition-all duration-200"
        >
          搜索数据
        </button>
      </div>
    </div>

    <!-- 数据表格 - 现代设计 -->
    <div class="glass-card overflow-hidden animate-in" style="animation-delay: 100ms">
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="space-y-4 text-center">
          <div class="w-12 h-12 mx-auto border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin"></div>
          <p :class="themeStore.isDark ? 'text-gray-400 text-sm' : 'text-gray-500 text-sm'">加载数据中...</p>
        </div>
      </div>

      <div v-else class="overflow-x-auto scrollbar-hide">
        <table class="data-table-modern">
          <thead>
            <tr>
              <th>平台</th>
              <th>地区</th>
              <th>达人</th>
              <th>标题</th>
              <th class="text-right">价格($)</th>
              <th>发布日期</th>
              <th class="text-right">播放量</th>
              <th class="text-right">点赞数</th>
              <th>状态</th>
              <th class="text-center">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(video, index) in videos" :key="video.id" class="group animate-in" :style="{ animationDelay: `${index * 50}ms` }">
              <td>
                <span
                  class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-semibold tracking-wide"
                  :class="getPlatformClass(video.platform)"
                >
                  {{ video.platform?.toUpperCase() }}
                </span>
              </td>
              <td :class="themeStore.isDark ? 'font-mono text-xs text-gray-400' : 'font-mono text-xs text-gray-500'">{{ getRegionName(video.region) }}</td>
              <td :class="themeStore.isDark ? 'font-medium text-white' : 'font-medium text-gray-900'">{{ video.influencer_name }}</td>
              <td :class="themeStore.isDark ? 'max-w-[200px] truncate text-gray-400' : 'max-w-[200px] truncate text-gray-600'">{{ video.title || '-' }}</td>
              <td class="text-right font-mono text-cyber-green font-semibold">${{ video.price_usd || '0' }}</td>
              <td :class="themeStore.isDark ? 'text-sm text-gray-500 whitespace-nowrap' : 'text-sm text-gray-500 whitespace-nowrap'">{{ formatDate(video.publish_date) }}</td>
              <td class="text-right font-mono text-cyber-blue">{{ formatNumber(video.play_count) }}</td>
              <td class="text-right font-mono text-pink-400">{{ formatNumber(video.like_count) }}</td>
              <td>
                <span
                  class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium"
                  :class="getStatusClass(video.status)"
                >
                  {{ getStatusName(video.status) }}
                </span>
              </td>
              <td>
                <div class="flex items-center justify-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <button
                    @click="editVideo(video)"
                    class="p-1.5 rounded-lg hover:bg-cyber-blue/10 text-cyber-blue transition-colors"
                    title="编辑"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    @click="deleteVideo(video)"
                    class="p-1.5 rounded-lg hover:bg-red-500/10 text-red-400 transition-colors"
                    title="删除"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                  <button
                    v-if="video.video_url"
                    @click="openVideo(video.video_url)"
                    class="p-1.5 rounded-lg hover:bg-cyber-purple/10 text-cyber-purple transition-colors"
                    title="查看"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="videos.length === 0">
              <td colspan="10" class="text-center py-20">
                <div class="space-y-3">
                  <div class="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-primary-500/10 to-cyber-purple/10 flex items-center justify-center">
                    <svg class="w-10 h-10 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <p :class="themeStore.isDark ? 'text-gray-500 text-sm' : 'text-gray-500 text-sm'">暂无视频数据</p>
                  <button @click="showCreateDialog" class="cyber-button text-sm px-4 py-2">
                    添加第一条视频
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页器 -->
      <div v-if="total > 0" :class="themeStore.isDark ? 'flex items-center justify-between px-6 py-4 border-t border-white/5' : 'flex items-center justify-between px-6 py-4 border-t border-gray-200'">
        <div :class="themeStore.isDark ? 'text-sm text-gray-500' : 'text-sm text-gray-500'">
          共 <span :class="themeStore.isDark ? 'text-white font-semibold' : 'text-gray-900 font-semibold'">{{ total }}</span> 条记录
        </div>
        <div class="flex items-center gap-4">
          <select
            v-model="pageSize"
            @change="fetchVideos"
            :class="themeStore.isDark
              ? 'px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-sm text-gray-300 focus:outline-none focus:border-cyber-blue/50'
              : 'px-3 py-1.5 rounded-lg bg-white border border-gray-200 text-sm text-gray-700 focus:outline-none focus:border-cyber-blue/50'"
          >
            <option :value="10" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">10条/页</option>
            <option :value="20" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">20条/页</option>
            <option :value="50" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">50条/页</option>
            <option :value="100" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">100条/页</option>
          </select>
          <div class="flex items-center gap-2">
            <button
              @click="currentPage > 1 && (currentPage--, fetchVideos())"
              :disabled="currentPage === 1"
              :class="themeStore.isDark
                ? 'p-2 rounded-lg hover:bg-white/5 disabled:opacity-30 disabled:cursor-not-allowed transition-all'
                : 'p-2 rounded-lg hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-all'"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <span :class="themeStore.isDark ? 'text-sm text-gray-400 min-w-[80px] text-center' : 'text-sm text-gray-500 min-w-[80px] text-center'">
              第 <span :class="themeStore.isDark ? 'text-white font-medium' : 'text-gray-900 font-medium'">{{ currentPage }}</span> / {{ Math.ceil(total / pageSize) }} 页
            </span>
            <button
              @click="currentPage < Math.ceil(total / pageSize) && (currentPage++, fetchVideos())"
              :disabled="currentPage >= Math.ceil(total / pageSize)"
              :class="themeStore.isDark
                ? 'p-2 rounded-lg hover:bg-white/5 disabled:opacity-30 disabled:cursor-not-allowed transition-all'
                : 'p-2 rounded-lg hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-all'"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 新增/编辑对话框 - 全屏模态 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="dialogVisible" class="fixed inset-0 z-50 overflow-y-auto" @click.self="dialogVisible = false">
          <!-- 背景遮罩 -->
          <div class="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity" />

          <!-- 对话框内容 -->
          <div class="relative min-h-screen flex items-center justify-center p-4">
            <div class="relative w-full max-w-4xl glass-card p-8 animate-slide-up max-h-[90vh] overflow-y-auto scrollbar-hide">
              <!-- 关闭按钮 -->
              <button
                @click="dialogVisible = false"
                :class="themeStore.isDark
                  ? 'absolute top-6 right-6 p-2 rounded-xl hover:bg-white/10 text-gray-400 hover:text-white transition-colors'
                  : 'absolute top-6 right-6 p-2 rounded-xl hover:bg-gray-100 text-gray-400 hover:text-gray-700 transition-colors'"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>

              <!-- 标题 -->
              <div class="mb-8">
                <h2 class="text-2xl font-bold gradient-text mb-2">
                  {{ isEdit ? '编辑视频' : '新增视频' }}
                </h2>
                <p v-if="!isEdit" :class="themeStore.isDark ? 'text-sm text-gray-400 flex items-center gap-2' : 'text-sm text-gray-500 flex items-center gap-2'">
                  <span class="w-1.5 h-1.5 rounded-full bg-cyber-blue animate-pulse"></span>
                  可粘贴链接并点击「抓取数据」自动填充信息
                </p>
              </div>

              <!-- 表单 -->
              <form @submit.prevent="handleSubmit" class="space-y-8">
                <!-- 视频链接区域 -->
                <div class="space-y-4">
                  <div class="flex items-center gap-3">
                    <span class="w-1.5 h-5 rounded-full bg-gradient-to-b from-cyber-blue to-cyber-purple"></span>
                    <h3 :class="themeStore.isDark ? 'text-sm font-semibold text-gray-300 uppercase tracking-wider' : 'text-sm font-semibold text-gray-600 uppercase tracking-wider'">视频链接（可选）</h3>
                  </div>
                  <div class="flex gap-3">
                    <input
                      v-model="form.video_url"
                      type="url"
                      placeholder="粘贴 TikTok / Instagram / YouTube 链接..."
                      :class="themeStore.isDark
                        ? 'flex-1 px-5 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 placeholder-gray-600 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all'
                        : 'flex-1 px-5 py-3 rounded-xl bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all'"
                    />
                    <button
                      type="button"
                      @click="fetchMetadataInDialog"
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
                    <span class="w-1.5 h-5 rounded-full bg-gradient-to-b from-cyber-purple to-pink-500"></span>
                    <h3 :class="themeStore.isDark ? 'text-sm font-semibold text-gray-300 uppercase tracking-wider' : 'text-sm font-semibold text-gray-600 uppercase tracking-wider'">基本信息</h3>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div class="space-y-1.5">
                      <label :class="themeStore.isDark ? 'text-xs text-gray-500 font-medium' : 'text-xs text-gray-600 font-medium'">平台 *</label>
                      <select
                        v-model="form.platform"
                        required
                        :class="themeStore.isDark
                          ? 'w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 focus:border-cyber-purple/50 focus:outline-none focus:ring-2 focus:ring-cyber-purple/20 transition-all'
                          : 'w-full px-4 py-3 rounded-xl bg-white border border-gray-200 text-gray-700 focus:border-cyber-purple/50 focus:outline-none focus:ring-2 focus:ring-cyber-purple/20 transition-all'"
                      >
                        <option value="tiktok" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">TikTok</option>
                        <option value="ins" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">Instagram</option>
                        <option value="youtube" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">YouTube</option>
                      </select>
                    </div>

                    <div class="space-y-1.5">
                      <label :class="themeStore.isDark ? 'text-xs text-gray-500 font-medium' : 'text-xs text-gray-600 font-medium'">地区</label>
                      <select
                        v-model="form.region"
                        :class="themeStore.isDark
                          ? 'w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 focus:border-cyber-purple/50 focus:outline-none focus:ring-2 focus:ring-cyber-purple/20 transition-all'
                          : 'w-full px-4 py-3 rounded-xl bg-white border border-gray-200 text-gray-700 focus:border-cyber-purple/50 focus:outline-none focus:ring-2 focus:ring-cyber-purple/20 transition-all'"
                      >
                        <option value="" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">选择地区</option>
                        <option v-for="r in regionOptions" :key="r.value" :value="r.value" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">{{ r.label }}</option>
                      </select>
                    </div>

                    <div class="space-y-1.5">
                      <label :class="themeStore.isDark ? 'text-xs text-gray-500 font-medium' : 'text-xs text-gray-600 font-medium'">达人名称 *</label>
                      <input
                        v-model="form.influencer_name"
                        type="text"
                        required
                        placeholder="输入达人名称"
                        :class="themeStore.isDark
                          ? 'w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 placeholder-gray-600 focus:border-cyber-purple/50 focus:outline-none focus:ring-2 focus:ring-cyber-purple/20 transition-all'
                          : 'w-full px-4 py-3 rounded-xl bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-purple/50 focus:outline-none focus:ring-2 focus:ring-cyber-purple/20 transition-all'"
                      />
                    </div>

                    <div class="space-y-1.5">
                      <label :class="themeStore.isDark ? 'text-xs text-gray-500 font-medium' : 'text-xs text-gray-600 font-medium'">内容方向</label>
                      <select
                        v-model="form.content_direction"
                        :class="themeStore.isDark
                          ? 'w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 focus:border-cyber-purple/50 focus:outline-none focus:ring-2 focus:ring-cyber-purple/20 transition-all'
                          : 'w-full px-4 py-3 rounded-xl bg-white border border-gray-200 text-gray-700 focus:border-cyber-purple/50 focus:outline-none focus:ring-2 focus:ring-cyber-purple/20 transition-all'"
                      >
                        <option value="" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">选择方向</option>
                        <option v-for="d in directionOptions" :key="d.value" :value="d.value" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">{{ d.label }}</option>
                      </select>
                    </div>

                    <div class="space-y-1.5">
                      <label :class="themeStore.isDark ? 'text-xs text-gray-500 font-medium' : 'text-xs text-gray-600 font-medium'">合作价格 ($)</label>
                      <input
                        v-model.number="form.price_usd"
                        type="number"
                        step="0.01"
                        min="0"
                        placeholder="输入价格"
                        :class="themeStore.isDark
                          ? 'w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 placeholder-gray-600 focus:border-cyber-purple/50 focus:outline-none focus:ring-2 focus:ring-cyber-purple/20 transition-all'
                          : 'w-full px-4 py-3 rounded-xl bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-purple/50 focus:outline-none focus:ring-2 focus:ring-cyber-purple/20 transition-all'"
                      />
                    </div>

                    <div class="space-y-1.5">
                      <label :class="themeStore.isDark ? 'text-xs text-gray-500 font-medium' : 'text-xs text-gray-600 font-medium'">标题</label>
                      <input
                        v-model="form.title"
                        type="text"
                        placeholder="输入视频标题"
                        :class="themeStore.isDark
                          ? 'w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 placeholder-gray-600 focus:border-cyber-purple/50 focus:outline-none focus:ring-2 focus:ring-cyber-purple/20 transition-all'
                          : 'w-full px-4 py-3 rounded-xl bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-purple/50 focus:outline-none focus:ring-2 focus:ring-cyber-purple/20 transition-all'"
                      />
                    </div>

                    <div class="space-y-1.5">
                      <label :class="themeStore.isDark ? 'text-xs text-gray-500 font-medium' : 'text-xs text-gray-600 font-medium'">发布日期</label>
                      <input
                        v-model="form.publish_date"
                        type="date"
                        :class="themeStore.isDark
                          ? 'w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 focus:border-cyber-purple/50 focus:outline-none focus:ring-2 focus:ring-cyber-purple/20 transition-all'
                          : 'w-full px-4 py-3 rounded-xl bg-white border border-gray-200 text-gray-700 focus:border-cyber-purple/50 focus:outline-none focus:ring-2 focus:ring-cyber-purple/20 transition-all'"
                      />
                    </div>

                    <div class="space-y-1.5">
                      <label :class="themeStore.isDark ? 'text-xs text-gray-500 font-medium' : 'text-xs text-gray-600 font-medium'">状态</label>
                      <select
                        v-model="form.status"
                        :class="themeStore.isDark
                          ? 'w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 focus:border-cyber-purple/50 focus:outline-none focus:ring-2 focus:ring-cyber-purple/20 transition-all'
                          : 'w-full px-4 py-3 rounded-xl bg-white border border-gray-200 text-gray-700 focus:border-cyber-purple/50 focus:outline-none focus:ring-2 focus:ring-cyber-purple/20 transition-all'"
                      >
                        <option v-for="s in statusOptions" :key="s.value" :value="s.value" :class="themeStore.isDark ? 'bg-gray-900' : 'bg-white'">{{ s.label }}</option>
                      </select>
                    </div>
                  </div>
                </div>

                <!-- 数据指标 -->
                <div class="space-y-4">
                  <div class="flex items-center gap-3">
                    <span class="w-1.5 h-5 rounded-full bg-gradient-to-b from-cyber-green to-emerald-500"></span>
                    <h3 :class="themeStore.isDark ? 'text-sm font-semibold text-gray-300 uppercase tracking-wider' : 'text-sm font-semibold text-gray-600 uppercase tracking-wider'">数据指标</h3>
                  </div>

                  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="space-y-1.5">
                      <label :class="themeStore.isDark ? 'text-xs text-gray-500 font-medium' : 'text-xs text-gray-600 font-medium'">播放量</label>
                      <input
                        v-model.number="form.play_count"
                        type="number"
                        min="0"
                        placeholder="0"
                        :class="themeStore.isDark
                          ? 'w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 placeholder-gray-600 focus:border-cyber-green/50 focus:outline-none focus:ring-2 focus:ring-cyber-green/20 transition-all'
                          : 'w-full px-4 py-2.5 rounded-xl bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-green/50 focus:outline-none focus:ring-2 focus:ring-cyber-green/20 transition-all'"
                      />
                    </div>
                    <div class="space-y-1.5">
                      <label :class="themeStore.isDark ? 'text-xs text-gray-500 font-medium' : 'text-xs text-gray-600 font-medium'">点赞数</label>
                      <input
                        v-model.number="form.like_count"
                        type="number"
                        min="0"
                        placeholder="0"
                        :class="themeStore.isDark
                          ? 'w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 placeholder-gray-600 focus:border-cyber-green/50 focus:outline-none focus:ring-2 focus:ring-cyber-green/20 transition-all'
                          : 'w-full px-4 py-2.5 rounded-xl bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-green/50 focus:outline-none focus:ring-2 focus:ring-cyber-green/20 transition-all'"
                      />
                    </div>
                    <div class="space-y-1.5">
                      <label :class="themeStore.isDark ? 'text-xs text-gray-500 font-medium' : 'text-xs text-gray-600 font-medium'">评论数</label>
                      <input
                        v-model.number="form.comment_count"
                        type="number"
                        min="0"
                        placeholder="0"
                        :class="themeStore.isDark
                          ? 'w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 placeholder-gray-600 focus:border-cyber-green/50 focus:outline-none focus:ring-2 focus:ring-cyber-green/20 transition-all'
                          : 'w-full px-4 py-2.5 rounded-xl bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-green/50 focus:outline-none focus:ring-2 focus:ring-cyber-green/20 transition-all'"
                      />
                    </div>
                    <div class="space-y-1.5">
                      <label :class="themeStore.isDark ? 'text-xs text-gray-500 font-medium' : 'text-xs text-gray-600 font-medium'">分享数</label>
                      <input
                        v-model.number="form.share_count"
                        type="number"
                        min="0"
                        placeholder="0"
                        :class="themeStore.isDark
                          ? 'w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 placeholder-gray-600 focus:border-cyber-green/50 focus:outline-none focus:ring-2 focus:ring-cyber-green/20 transition-all'
                          : 'w-full px-4 py-2.5 rounded-xl bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-green/50 focus:outline-none focus:ring-2 focus:ring-cyber-green/20 transition-all'"
                      />
                    </div>
                  </div>
                </div>

                <!-- 联系方式 -->
                <div class="space-y-4">
                  <div class="flex items-center gap-3">
                    <span class="w-1.5 h-5 rounded-full bg-gradient-to-b from-pink-500 to-rose-500"></span>
                    <h3 :class="themeStore.isDark ? 'text-sm font-semibold text-gray-300 uppercase tracking-wider' : 'text-sm font-semibold text-gray-600 uppercase tracking-wider'">联系方式</h3>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div class="space-y-1.5">
                      <label :class="themeStore.isDark ? 'text-xs text-gray-500 font-medium' : 'text-xs text-gray-600 font-medium'">邮箱</label>
                      <input
                        v-model="form.contact_email"
                        type="email"
                        placeholder="联系邮箱地址"
                        :class="themeStore.isDark
                          ? 'w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 placeholder-gray-600 focus:border-pink-500/50 focus:outline-none focus:ring-2 focus:ring-pink-500/20 transition-all'
                          : 'w-full px-4 py-3 rounded-xl bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-pink-500/50 focus:outline-none focus:ring-2 focus:ring-pink-500/20 transition-all'"
                      />
                    </div>
                    <div class="space-y-1.5">
                      <label :class="themeStore.isDark ? 'text-xs text-gray-500 font-medium' : 'text-xs text-gray-600 font-medium'">WhatsApp</label>
                      <input
                        v-model="form.contact_whatsapp"
                        type="tel"
                        placeholder="WhatsApp号码"
                        :class="themeStore.isDark
                          ? 'w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 placeholder-gray-600 focus:border-pink-500/50 focus:outline-none focus:ring-2 focus:ring-pink-500/20 transition-all'
                          : 'w-full px-4 py-3 rounded-xl bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-pink-500/50 focus:outline-none focus:ring-2 focus:ring-pink-500/20 transition-all'"
                      />
                    </div>
                  </div>
                </div>

                <!-- 提交按钮 -->
                <div :class="themeStore.isDark ? 'flex justify-end gap-4 pt-6 border-t border-white/5' : 'flex justify-end gap-4 pt-6 border-t border-gray-200'">
                  <button
                    type="button"
                    @click="dialogVisible = false"
                    :class="themeStore.isDark
                      ? 'px-8 py-3 rounded-xl text-sm font-medium text-gray-400 hover:text-white hover:bg-white/5 border border-white/10 hover:border-white/20 transition-all duration-200'
                      : 'px-8 py-3 rounded-xl text-sm font-medium text-gray-500 hover:text-gray-900 hover:bg-gray-100 border border-gray-200 hover:border-gray-300 transition-all duration-200'"
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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'

const userStore = useUserStore()
const themeStore = useThemeStore()
const loading = ref(false)
const videos = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dateRange = ref([])

const filters = reactive({
  platform: '',
  region: '',
  influencer_name: '',
  status: ''
})

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const formRef = ref()
const fetching = ref(false)

const currentUser = computed(() => userStore.user?.username || '')
const userRole = computed(() => userStore.user?.role || '')

const canSelectAllUsers = computed(() => {
  return ['admin', 'manager'].includes(userRole.value)
})

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
  { value: 'FF', label: 'Free Fire' },
  { value: 'MLBB', label: 'Mobile Legends' }
]

const statusOptions = [
  { value: 'pending_review', label: '待审核' },
  { value: 'pending_publish', label: '待发布' },
  { value: 'published', label: '已发布' },
  { value: 'completed', label: '已完成' }
]

const defaultForm = {
  platform: 'tiktok',
  region: '',
  content_direction: '',
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

const rules = {
  platform: [{ required: true, message: '请选择平台', trigger: 'change' }],
  influencer_name: [{ required: true, message: '请输入达人名称', trigger: 'blur' }]
}

onMounted(async () => {
  fetchVideos()
  if (canSelectAllUsers.value) {
    await fetchUsers()
  }
})

async function fetchVideos() {
  loading.value = true

  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      sort_by: 'publish_date',
      sort_order: 'desc',
      ...filters
    }

    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const response = await api.get('/videos/', { params })
    videos.value = response.items || []
    total.value = response.total || 0
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
    console.warn('获取用户列表失败（非管理员无法查看用户列表）:', error.message)
    userList.value = []
  }
}

function resetFilters() {
  Object.assign(filters, {
    platform: '',
    region: '',
    influencer_name: '',
    status: ''
  })
  dateRange.value = []
  currentPage.value = 1
  fetchVideos()
}

function showCreateDialog() {
  isEdit.value = false
  editingId.value = null
  Object.assign(form, {
    ...defaultForm,
    publish_date: new Date().toISOString().split('T')[0],
    contact_person: canSelectAllUsers.value ? '' : currentUser.value
  })
  dialogVisible.value = true
}

function editVideo(video) {
  isEdit.value = true
  editingId.value = video.id
  Object.assign(form, {
    platform: video.platform,
    region: video.region,
    content_direction: video.content_direction,
    influencer_name: video.influencer_name,
    price_usd: video.price_usd,
    title: video.title,
    publish_date: video.publish_date ? video.publish_date.split('T')[0] : new Date().toISOString().split('T')[0],
    play_count: video.play_count,
    like_count: video.like_count,
    comment_count: video.comment_count,
    share_count: video.share_count,
    video_url: video.video_url,
    contact_person: video.contact_person,
    contact_email: video.contact_email,
    contact_whatsapp: video.contact_whatsapp,
    status: video.status
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  submitting.value = true

  try {
    const data = { ...form }

    if (isEdit.value) {
      await api.put(`/videos/${editingId.value}`, data)
      ElMessage.success('更新成功')
    } else {
      await api.post('/videos/', data)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    fetchVideos()
  } catch (error) {
    console.error('Submit error:', error)
  } finally {
    submitting.value = false
  }
}

function deleteVideo(video) {
  ElMessageBox.confirm(`确定要删除视频"${video.title || video.influencer_name}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/videos/${video.id}`)
      ElMessage.success('删除成功')
      fetchVideos()
    } catch (error) {
      console.error('Delete error:', error)
    }
  }).catch(() => {})
}

async function fetchMetadataInDialog() {
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
  } catch (error) {
    console.error('Fetch metadata error:', error)
    ElMessage.warning('抓取失败，请手动填写数据')
  } finally {
    fetching.value = false
  }
}

function openVideo(url) {
  window.open(url, '_blank')
}

function formatNumber(num) {
  if (!num) return '0'
  if (num >= 10000) return (num / 10000).toFixed(1) + 'w'
  return num.toLocaleString()
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function getPlatformType(platform) {
  const types = { tiktok: '', ins: 'success', youtube: 'warning' }
  return types[platform] || 'info'
}

function getStatusType(status) {
  const types = {
    pending_review: 'info',
    pending_publish: 'warning',
    published: '',
    completed: 'success'
  }
  return types[status] || 'info'
}

function getStatusName(status) {
  const names = {
    pending_review: '待审核',
    pending_publish: '待发布',
    published: '已发布',
    completed: '已完成'
  }
  return names[status] || status
}

function getRegionName(region) {
  const found = regionOptions.find(r => r.value === region)
  return found ? found.label : region || '-'
}

function getPlatformClass(platform) {
  if (themeStore.isDark) {
    const classes = {
      tiktok: 'bg-black/40 text-gray-200 border border-white/20',
      ins: 'bg-pink-500/10 text-pink-400 border border-pink-500/30',
      youtube: 'bg-red-500/10 text-red-400 border border-red-500/30'
    }
    return classes[platform] || 'bg-gray-500/10 text-gray-300 border border-gray-500/30'
  }
  const classes = {
    tiktok: 'bg-gray-100 text-gray-700 border border-gray-200',
    ins: 'bg-pink-50 text-pink-600 border border-pink-200',
    youtube: 'bg-red-50 text-red-600 border border-red-200'
  }
  return classes[platform] || 'bg-gray-100 text-gray-600 border border-gray-200'
}

function getStatusClass(status) {
  if (themeStore.isDark) {
    const classes = {
      pending_review: 'bg-blue-500/10 text-blue-400 border border-blue-500/30',
      pending_publish: 'bg-amber-500/10 text-amber-400 border border-amber-500/30',
      published: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30',
      completed: 'bg-purple-500/10 text-purple-400 border border-purple-500/30'
    }
    return classes[status] || 'bg-gray-500/10 text-gray-400 border border-gray-500/30'
  }
  const classes = {
    pending_review: 'bg-blue-50 text-blue-600 border border-blue-200',
    pending_publish: 'bg-amber-50 text-amber-600 border border-amber-200',
    published: 'bg-emerald-50 text-emerald-600 border border-emerald-200',
    completed: 'bg-purple-50 text-purple-600 border border-purple-200'
  }
  return classes[status] || 'bg-gray-100 text-gray-600 border border-gray-200'
}
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
