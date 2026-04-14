<template>
  <div v-if="total > 0" class="flex items-center justify-between px-6 py-4 dark:border-t dark:border-white/5 border-t border-gray-200">
    <div class="text-sm dark:text-gray-500 text-gray-500">
      共 <span class="dark:text-white text-gray-900 font-semibold">{{ total }}</span> 条记录
    </div>
    <div class="flex items-center gap-4">
      <select
        v-if="showPageSize"
        :value="pageSize"
        @change="$emit('update:pageSize', Number($event.target.value))"
        class="px-3 py-1.5 rounded-lg dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-sm text-gray-700 focus:outline-none focus:border-cyber-blue/50"
      >
        <option v-for="size in pageSizeOptions" :key="size" :value="size" class="dark:bg-gray-900 bg-white">{{ size }}条/页</option>
      </select>
      <div class="flex items-center gap-2">
        <button
          @click="changePage(modelValue - 1)"
          :disabled="modelValue <= 1"
          class="p-2 rounded-lg dark:hover:bg-white/5 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <span class="text-sm dark:text-gray-400 text-gray-500 min-w-[80px] text-center">
          第 <span class="dark:text-white text-gray-900 font-medium">{{ modelValue }}</span> / {{ totalPages }} 页
        </span>
        <button
          @click="changePage(modelValue + 1)"
          :disabled="modelValue >= totalPages"
          class="p-2 rounded-lg dark:hover:bg-white/5 hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Number, default: 1 },
  total: { type: Number, default: 0 },
  pageSize: { type: Number, default: 20 },
  showPageSize: { type: Boolean, default: false },
  pageSizeOptions: { type: Array, default: () => [10, 20, 50, 100] }
})

const emit = defineEmits(['update:modelValue', 'update:pageSize', 'change'])

const totalPages = computed(() => Math.ceil(props.total / props.pageSize) || 1)

function changePage(page) {
  if (page < 1 || page > totalPages.value) return
  emit('update:modelValue', page)
  emit('change', page)
}
</script>
