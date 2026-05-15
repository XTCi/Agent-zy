<template>
  <div class="register-container">
    <el-card class="register-card">
      <h2>用户注册</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" />
        </el-form-item>
      </el-form>
      <div class="register-actions">
        <el-button type="primary" @click="handleRegister">注册</el-button>
        <el-button type="text" @click="$router.push('/login')">返回登录</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { register } from '@/api/user';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

const router = useRouter();
const formRef = ref();
const form = ref({ username: '', email: '', password: '' });
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
};

const handleRegister = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const res = await register(form.value);
        if (res.data && res.data.code === 1) {
          ElMessage.success('注册成功，请登录');
          router.push('/login');
        } else {
          ElMessage.error(res.data.message || '注册失败');
        }
      } catch (e) {
        ElMessage.error('注册失败');
      }
    }
  });
};
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
}
.register-card {
  width: 350px;
  padding: 32px 24px 24px 24px;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.08);
}
.register-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
}
</style>