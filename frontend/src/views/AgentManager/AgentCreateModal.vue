<template>
  <el-dialog v-model="visible" title="创建智能体" width="400px" @close="$emit('close')">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
      <el-form-item label="头像" prop="photo">
        <el-upload
          class="avatar-uploader"
          action="#"
          :auto-upload="false"
          :show-file-list="false"
          :on-change="handleAvatarChange"
        >
          <img v-if="form.photo" :src="form.photo" class="avatar" />
          <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
        </el-upload>
      </el-form-item>
      <el-form-item label="名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入智能体名称" />
      </el-form-item>
      <el-form-item label="介绍" prop="introduce">
        <el-input v-model="form.introduce" placeholder="请输入智能体介绍" />
      </el-form-item>
      <el-form-item label="开场白" prop="prologue">
        <el-input v-model="form.prologue" placeholder="请输入开场白" />
      </el-form-item>
      <el-form-item label="角色设定" prop="role_setting">
        <el-input v-model="form.role_setting" type="textarea" placeholder="请输入角色设定" />
      </el-form-item>
      <el-form-item label="温度" prop="temperature">
        <el-input-number v-model="form.temperature" :min="0" :max="1" :step="0.1" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('close')">取消</el-button>
      <el-button type="primary" @click="handleCreate" :loading="loading">创建</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue';
import { createAgent, uploadAgentPhoto } from '@/api/agent';
import { Plus } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

const visible = ref(true);
const loading = ref(false);
const formRef = ref();

const form = ref({
  name: '',
  role_setting: '',
  temperature: 0.0,
  introduce: '',
  prologue: '',
  photo: '',
  avatar_extension: '',
  original_filename: '',
  photo_extension: ''
});
const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  role_setting: [{ required: true, message: '请输入角色设定', trigger: 'blur' }],
  introduce: [{ required: true, message: '请输入介绍', trigger: 'blur' }],
  prologue: [{ required: true, message: '请输入开场白', trigger: 'blur' }]
};
const emit = defineEmits(['close', 'created']);

const handleAvatarChange = (file) => {
  const reader = new FileReader();
  reader.onload = (e) => {
    form.value.photo = e.target.result;
  };
  reader.readAsDataURL(file.raw);
  // 保存文件扩展名
  const extension = file.raw.name.split('.').pop().toLowerCase();
  form.value.photo_extension = extension;
};

const handleCreate = async () => {
  if (!formRef.value) return;

  try {
    await formRef.value.validate();
    loading.value = true;

    // 1. 如果有头像，先上传头像
    if (form.value.photo && form.value.photo.startsWith('data:')) {
      const formData = new FormData();
      const blob = await fetch(form.value.photo).then(r => r.blob());
      // 使用原始文件名，包含扩展名
      const filename = `avatar.${form.value.photo_extension}`;
      formData.append('file', blob, filename);

      console.log('开始上传头像...');
      const uploadRes = await uploadAgentPhoto(formData);
      console.log('头像上传响应:', uploadRes);

      if (uploadRes && uploadRes.data && uploadRes.data.photo_url) {
        form.value.photo = uploadRes.data.photo_url;
        console.log('设置头像URL:', form.value.photo);
      } else {
        console.error('头像上传响应格式不正确:', uploadRes);
        throw new Error('头像上传失败：响应格式不正确');
      }
    }

    // 2. 创建智能体
    console.log('开始创建智能体，数据:', form.value);
    const createRes = await createAgent(form.value);
    console.log('创建智能体响应:', createRes);

    if (createRes.code === 1) {
      ElMessage.success('创建成功');
      emit('created');
      emit('close');
    } else {
      throw new Error(createRes.message || '创建失败');
    }
  } catch (error) {
    console.error('操作失败:', error);
    ElMessage.error(error.message || '操作失败');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.avatar-uploader {
  text-align: center;
}
.avatar-uploader .avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
}
.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 100px;
  height: 100px;
}
.avatar-uploader .el-upload:hover {
  border-color: #409EFF;
}
.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  line-height: 100px;
  text-align: center;
}
</style>