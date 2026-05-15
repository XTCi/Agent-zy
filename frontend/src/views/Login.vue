<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2>用户登录</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" />
        </el-form-item>
      </el-form>
      <div class="login-actions">
        <el-button type="primary" @click="handleLogin">登录</el-button>
        <el-button type="text" @click="$router.push('/register')">注册</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { login } from '@/api/user';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

const router = useRouter();
const formRef = ref();
const form = ref({ username: '', password: '' });
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
};

const handleLogin = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const res = await login(form.value);
        if (res.data && res.data.data && res.data.data.access_token) {
          localStorage.setItem('token', res.data.data.access_token);
          window.dispatchEvent(new Event('storage'));
          ElMessage.success('登录成功');
          router.push('/agent-manager');
        } else {
          ElMessage.error(res.data.message || '登录失败');
        }
      } catch (e) {
        ElMessage.error('登录失败');
      }
    }
  });
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
}
.login-card {
  width: 350px;
  padding: 32px 24px 24px 24px;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.08);
}
.login-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
}
</style>