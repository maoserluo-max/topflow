<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="aside">
      <div class="logo">
        <h2>顶流 TopFlow</h2>
        <p>达人营销管理系统</p>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#001529"
        text-color="#fff"
        active-text-color="#1890ff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/videos">
          <el-icon><VideoPlay /></el-icon>
          <span>视频管理</span>
        </el-menu-item>
        <el-menu-item index="/users" v-if="userStore.isAdmin">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/logs" v-if="userStore.isAdmin">
          <el-icon><Document /></el-icon>
          <span>操作日志</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ $route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" icon="UserFilled" />
              <span>{{ userStore.user?.full_name || userStore.user?.username }}</span>
              <el-tag size="small" :type="getRoleType(userStore.user?.role)" style="margin-left: 8px;">
                {{ getRoleName(userStore.user?.role) }}
              </el-tag>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useUserStore } from '@/stores/user'
import { DataAnalysis, VideoPlay, User, Document } from '@element-plus/icons-vue'

const userStore = useUserStore()

function getRoleType(role) {
  const types = { admin: 'danger', manager: 'warning', user: 'info' }
  return types[role] || 'info'
}

function getRoleName(role) {
  const names = { admin: '管理员', manager: '经理', user: '用户' }
  return names[role] || role
}

function handleCommand(command) {
  if (command === 'logout') {
    userStore.logout()
    window.location.href = '/login'
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.aside {
  background-color: #001529;
  overflow-y: auto;
}

.logo {
  padding: 20px;
  text-align: center;
  color: #fff;
  border-bottom: 1px solid #1f1f1f;
}

.logo h2 {
  font-size: 20px;
  margin-bottom: 5px;
}

.logo p {
  font-size: 12px;
  color: #999;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 64px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 8px;
}

.main {
  background-color: #f0f2f5;
  padding: 24px;
}
</style>