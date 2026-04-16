<template>
  <div>
    <div
      class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group hover:dark:bg-white/[0.03] hover:bg-gray-50"
      :style="{ paddingLeft: `${level * 28 + 16}px` }"
    >
      <!-- 展开/收起按钮 -->
      <button
        v-if="hasChildren"
        @click="expanded = !expanded"
        class="w-5 h-5 flex items-center justify-center rounded dark:text-gray-400 text-gray-500 dark:hover:bg-white/10 hover:bg-gray-200 transition-all"
        :class="{ 'rotate-0': expanded, '-rotate-90': !expanded }"
        style="transition: transform 0.2s"
      >
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
      </button>
      <div v-else class="w-5"></div>

      <!-- 连接线 -->
      <div v-if="level > 0" class="w-4 h-px dark:bg-white/10 bg-gray-200"></div>

      <!-- 头像 -->
      <div
        class="w-9 h-9 rounded-xl flex items-center justify-center text-sm font-bold uppercase flex-shrink-0"
        :class="getAvatarClass(user.role)"
      >
        {{ (user.username || 'U').charAt(0) }}
      </div>

      <!-- 用户信息 -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <span class="font-medium dark:text-white text-gray-900 text-sm">{{ user.full_name || user.username }}</span>
          <span class="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold" :class="getRoleClass(user.role)">
            {{ getRoleName(user.role) }}
          </span>
          <span v-if="!user.is_active" class="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold dark:bg-red-500/15 dark:text-red-400 bg-red-50 text-red-600">已禁用</span>
        </div>
        <div class="flex items-center gap-3 mt-0.5">
          <span class="text-xs dark:text-gray-500 text-gray-400">@{{ user.username }}</span>
          <div v-if="user.ancestor_chain && user.ancestor_chain.length > 0" class="flex items-center gap-1 text-[10px]">
            <svg class="w-2.5 h-2.5 dark:text-gray-600 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
            <span class="dark:text-gray-500 text-gray-400">
              {{ user.ancestor_chain.map(a => a.full_name || a.username).join(' → ') }}
            </span>
          </div>
        </div>
      </div>

      <!-- 项目权限 -->
      <div class="flex items-center gap-1.5">
        <span
          v-for="p in getUserProjects(user)"
          :key="p"
          class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium dark:bg-primary-500/10 dark:text-primary-300 bg-primary-50 text-primary-600"
        >{{ p }}</span>
      </div>

      <!-- 下属数 -->
      <div v-if="user.children_count > 0" class="flex items-center gap-1">
        <svg class="w-3.5 h-3.5 dark:text-gray-500 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
        <span class="text-xs dark:text-gray-400 text-gray-500">{{ user.children_count }}</span>
      </div>

      <!-- 操作按钮 -->
      <div class="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        <button @click="$emit('edit', user)" class="p-1.5 rounded-lg hover:bg-cyber-blue/10 text-cyber-blue transition-colors" title="编辑">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
        </button>
        <button
          @click="$emit('toggleStatus', user)"
          class="p-1.5 rounded-lg transition-colors"
          :class="user.is_active ? 'hover:bg-amber-500/10 text-amber-400' : 'hover:bg-emerald-500/10 text-emerald-400'"
          :title="user.is_active ? '禁用' : '启用'"
        >
          <svg v-if="user.is_active" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" /></svg>
          <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </button>
        <button
          v-if="canDelete"
          @click="$emit('delete', user)"
          class="p-1.5 rounded-lg hover:bg-red-500/10 text-red-400 transition-colors"
          title="删除"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
        </button>
      </div>
    </div>

    <!-- 子节点 -->
    <div v-if="expanded && hasChildren" class="relative">
      <div
        class="absolute top-0 bottom-0 dark:border-white/5 border-gray-200"
        :style="{ left: `${level * 28 + 34}px`, borderLeft: '1px dashed' }"
      ></div>
      <UserTreeNode
        v-for="child in children"
        :key="child.id"
        :user="child"
        :all-users="allUsers"
        :level="level + 1"
        :current-user="currentUser"
        @edit="$emit('edit', $event)"
        @toggle-status="$emit('toggleStatus', $event)"
        @delete="$emit('delete', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  user: { type: Object, required: true },
  allUsers: { type: Array, default: () => [] },
  level: { type: Number, default: 0 },
  currentUser: { type: Object, default: null }
})

defineEmits(['edit', 'toggleStatus', 'delete'])

const expanded = ref(true)

const ROLE_HIERARCHY = { super_admin: 4, admin: 3, leader: 2, user: 1 }

const children = computed(() => {
  return props.allUsers.filter(u => u.parent_id === props.user.id)
})

const hasChildren = computed(() => children.value.length > 0)

const canDelete = computed(() => {
  const myRole = props.currentUser?.role || ''
  const myLevel = ROLE_HIERARCHY[myRole] || 1
  const userLevel = ROLE_HIERARCHY[props.user.role] || 1
  if (props.user.id === props.currentUser?.id) return false
  if (props.user.role === 'super_admin') return false
  // 组长及以上可以删除级别低于自己的用户
  return myLevel > userLevel
})

function getUserProjects(user) {
  if (!user.projects) return ['Gamoji', 'Poseme', '内容孵化']
  return user.projects.split(',').map(p => p.trim()).filter(p => p)
}

function getRoleName(role) {
  const names = { super_admin: '系统管理员', admin: '管理员', leader: '组长', user: '普通用户' }
  return names[role] || role
}

function getRoleClass(role) {
  const classes = {
    super_admin: 'dark:bg-purple-500/15 dark:text-purple-400 bg-purple-50 text-purple-600',
    admin: 'dark:bg-red-500/15 dark:text-red-400 bg-red-50 text-red-600',
    leader: 'dark:bg-amber-500/15 dark:text-amber-400 bg-amber-50 text-amber-600',
    user: 'dark:bg-blue-500/15 dark:text-blue-400 bg-blue-50 text-blue-600'
  }
  return classes[role] || 'dark:bg-gray-500/15 dark:text-gray-400 bg-gray-100 text-gray-600'
}

function getAvatarClass(role) {
  const classes = {
    super_admin: 'dark:from-purple-500/30 dark:to-pink-500/30 dark:text-purple-200 from-purple-100 to-pink-100 text-purple-600',
    admin: 'dark:from-red-500/30 dark:to-orange-500/30 dark:text-red-200 from-red-100 to-orange-100 text-red-600',
    leader: 'dark:from-amber-500/30 dark:to-yellow-500/30 dark:text-amber-200 from-amber-100 to-yellow-100 text-amber-600',
    user: 'dark:from-blue-500/30 dark:to-cyan-500/30 dark:text-blue-200 from-blue-100 to-cyan-100 text-blue-600'
  }
  return classes[role] || 'dark:from-gray-500/30 dark:to-gray-500/30 dark:text-gray-200 from-gray-100 to-gray-200 text-gray-600'
}
</script>
