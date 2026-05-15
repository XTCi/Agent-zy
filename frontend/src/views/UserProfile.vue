<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <h2>用户信息</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="form.full_name" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="新密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="如需修改请填写" />
        </el-form-item>
      </el-form>
      <div class="profile-actions">
        <el-button type="primary" @click="handleUpdate">保存修改</el-button>
        <el-popconfirm title="确定要删除账号吗？" @confirm="handleDelete">
          <template #reference>
            <el-button type="danger">删除账号</el-button>
          </template>
        </el-popconfirm>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getUserInfo, updateUser, deleteUser } from '@/api/user';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

const router = useRouter();
const formRef = ref();
const form = ref({ username: '', email: '', full_name: '', phone: '', password: '' });
const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ]
};

const fetchUser = async () => {
  const res = await getUserInfo();
  if (res.data && res.data.data && res.data.data.user) {
    Object.assign(form.value, res.data.data.user);
  }
};

const handleUpdate = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      const updateData = { ...form.value };
      if (!updateData.password) delete updateData.password;
      const res = await updateUser(updateData);
      if (res.data && res.data.code === 1) {
        ElMessage.success('信息更新成功');
        fetchUser();
      } else {
        ElMessage.error(res.data.message || '更新失败');
      }
    }
  });
};

const handleDelete = async () => {
  await deleteUser();
  ElMessage.success('账号已删除');
  localStorage.removeItem('token');
  router.push('/login');
};

onMounted(fetchUser);
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
}
.profile-card {
  width: 400px;
  padding: 32px 24px 24px 24px;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.08);
}
.profile-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
}
</style>