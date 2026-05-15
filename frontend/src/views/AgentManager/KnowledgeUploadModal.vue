<template>
  <el-dialog v-model="visible" title="知识库上传" width="400px" @close="$emit('close')">
    <el-upload
      class="upload-demo"
      drag
      action=""
      :http-request="uploadFiles"
      :multiple="true"
      :show-file-list="true"
      :auto-upload="false"
      :file-list="fileList"
      :on-change="handleChange"
      :before-upload="beforeUpload"
    >
      <i class="el-icon-upload"></i>
      <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
      <div class="el-upload__tip" slot="tip">支持 PDF、TXT、DOCX、XLSX 文件</div>
    </el-upload>
    <el-divider>或输入网页URL</el-divider>
    <el-form :inline="true" @submit.prevent="handleAddUrl">
      <el-form-item>
        <el-input v-model="url" placeholder="请输入网页URL" style="width: 300px" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="urlLoading" @click="handleAddUrl">添加</el-button>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('close')">取消</el-button>
      <el-button type="primary" @click="submitUpload">上传</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue';
import { uploadKnowledgeFiles, addUrlToKnowledge } from '@/api/agent';
import { ElMessage } from 'element-plus';

const props = defineProps({
  agentId: String
});
const emit = defineEmits(['close']);
const visible = ref(true);
const fileList = ref([]);
const url = ref('');
const urlLoading = ref(false);

const handleChange = (file, fileList_) => {
  fileList.value = fileList_;
};

const beforeUpload = (file) => {
  const allowed = [
    'application/pdf',
    'text/plain',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ];
  if (!allowed.includes(file.raw.type)) {
    ElMessage.error('仅支持 PDF、TXT、DOCX、XLSX 文件');
    return false;
  }
  return true;
};

const uploadFiles = async (option) => {
  // 不自动上传，手动处理
};

const submitUpload = async () => {
  if (!fileList.value.length) return;
  const formData = new FormData();
  fileList.value.forEach(f => formData.append('files', f.raw));
  await uploadKnowledgeFiles(formData);
  emit('close');
};

const handleAddUrl = async () => {
  if (!url.value) {
    ElMessage.warning('请输入URL');
    return;
  }
  urlLoading.value = true;
  try {
    const res = await addUrlToKnowledge(url.value);
    console.log('URL添加响应:', res); // 添加日志
    if (res && res.data && res.data.code === 1) {
      ElMessage.success(`网页内容学习成功，添加了 ${res.data.data.doc_count} 个文档`);
      url.value = '';
    } else {
      ElMessage.error(res.data?.message || '添加失败');
    }
  } catch (e) {
    console.error('URL添加错误:', e); // 添加错误日志
    ElMessage.error('添加失败');
  } finally {
    urlLoading.value = false;
  }
};
</script>

<style scoped>
.upload-demo {
  margin-bottom: 20px;
}
</style>