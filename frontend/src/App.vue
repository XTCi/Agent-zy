<script setup>
import { useRoute, useRouter } from 'vue-router'
import { ChatLineRound, Setting, User } from '@element-plus/icons-vue'
import { ref, computed } from 'vue'

const route = useRoute()
const router = useRouter()
const token = ref(localStorage.getItem('token'))

const isLogin = computed(() => !!token.value)

function logout() {
  localStorage.removeItem('token')
  token.value = ''
  router.push('/login')
}

window.addEventListener('storage', () => {
  token.value = localStorage.getItem('token')
})
</script>

<template>
  <div>
    <!-- 登录/注册/个人中心页面不显示任何主布局和用户栏 -->
    <template v-if="route.path === '/login' || route.path === '/register' || route.path === '/profile'">
      <router-view />
    </template>
    <!-- agent-manager 页面，登录后只显示个人中心和退出 -->
    <template v-else-if="route.path === '/agent-manager'">
      <div class="user-bar user-bar-agent">
        <el-dropdown v-if="isLogin">
          <span class="el-dropdown-link">
            <el-icon><User /></el-icon> 个人中心 <i class="el-icon-arrow-down el-icon--right"></i>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="$router.push('/profile')">账号信息</el-dropdown-item>
              <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
      <router-view />
    </template>
    <!-- 其他页面显示主布局和用户栏 -->
    <template v-else>
      <div class="user-bar">
        <template v-if="isLogin">
          <el-dropdown>
            <span class="el-dropdown-link">
              <el-icon><User /></el-icon> 个人中心 <i class="el-icon-arrow-down el-icon--right"></i>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="$router.push('/profile')">账号信息</el-dropdown-item>
                <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button type="text" @click="$router.push('/login')">登录</el-button>
          <el-button type="text" @click="$router.push('/register')">注册</el-button>
        </template>
      </div>
      <el-container class="app-container">
        <el-aside width="200px">
          <el-menu
            :router="true"
            class="sidebar-menu"
            default-active="/"
          >
            <el-menu-item index="/">
              <el-icon><ChatLineRound /></el-icon>
              <span>智能对话</span>
            </el-menu-item>
            <el-menu-item index="/settings">
              <el-icon><Setting /></el-icon>
              <span>知识库配置</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </template>
  </div>
</template>

<style>
.user-bar {
  position: fixed;
  top: 0;
  right: 0;
  z-index: 10;
  padding: 16px 32px 0 0;
  text-align: right;
  width: 100vw;
  display: flex;
  justify-content: flex-end;
}
.user-bar-agent {
  background: transparent;
  width: 100vw;
  padding: 16px 32px 0 0;
  position: fixed;
  top: 0;
  right: 0;
  z-index: 10;
  text-align: right;
  display: flex;
  justify-content: flex-end;
}
@media (max-width: 600px) {
  .user-bar, .user-bar-agent {
    padding: 8px 8px 0 0;
    font-size: 14px;
  }
}
.app-container {
  height: 100vh;
}

.sidebar-menu {
  height: 100%;
  border-right: solid 1px #e6e6e6;
}

.el-aside {
  background-color: #fff;
}

.el-main {
  padding: 20px;
  background-color: #f5f7fa;
}
</style>
