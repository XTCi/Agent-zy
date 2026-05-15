<template>
  <div class="settings-container">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>网页链接学习</span>
        </div>
      </template>
      <el-input
        v-model="webUrl"
        placeholder="请输入网页URL"
        :disabled="webLoading"
      >
        <template #append>
          <el-button @click="learnWeb" :loading="webLoading">学习</el-button>
        </template>
      </el-input>
    </el-card>

    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>PDF文件学习</span>
        </div>
      </template>
      <el-upload
        class="upload-demo"
        drag
        action="#"
        :auto-upload="false"
        :on-change="handlePdfChange"
        accept=".pdf"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
      </el-upload>
      <el-button
        type="primary"
        @click="uploadPdf"
        :disabled="!pdfFile"
        :loading="pdfLoading"
        style="margin-top: 16px"
      >
        上传并学习
      </el-button>
    </el-card>

    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>TXT文件学习</span>
        </div>
      </template>
      <el-upload
        class="upload-demo"
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleTxtChange"
        accept=".txt"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
      </el-upload>
      <el-button
        type="primary"
        @click="uploadTxt"
        :disabled="!txtFile"
        :loading="txtLoading"
        style="margin-top: 16px"
      >
        上传并学习
      </el-button>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { learnFromWebpage, learnFromPdf, learnFromTxt } from '../api'
import { ElMessage } from 'element-plus'

const webUrl = ref('')
const webLoading = ref(false)
const pdfFile = ref(null)
const pdfLoading = ref(false)
const txtFile = ref(null)
const txtLoading = ref(false)

const learnWeb = async () => {
  if (!webUrl.value) {
    ElMessage.warning('请输入网页URL')
    return
  }

  webLoading.value = true
  try {
    await learnFromWebpage(webUrl.value)
    ElMessage.success('网页学习成功')
    webUrl.value = ''
  } catch (error) {
    ElMessage.error('网页学习失败')
    console.error('Error:', error)
  } finally {
    webLoading.value = false
  }
}

const handlePdfChange = (file) => {
  pdfFile.value = file.raw
}

const uploadPdf = async () => {
  if (!pdfFile.value) return

  pdfLoading.value = true
  try {
    await learnFromPdf(pdfFile.value)
    ElMessage.success('PDF学习成功')
    pdfFile.value = null
  } catch (error) {
    ElMessage.error('PDF学习失败')
    console.error('Error:', error)
  } finally {
    pdfLoading.value = false
  }
}

const handleTxtChange = (file) => {
  txtFile.value = file.raw
}

const uploadTxt = async () => {
  if (!txtFile.value) return

  txtLoading.value = true
  try {
    await learnFromTxt(txtFile.value)
    ElMessage.success('TXT文件学习成功')
    txtFile.value = null
  } catch (error) {
    ElMessage.error('TXT文件学习失败')
    console.error('Error:', error)
  } finally {
    txtLoading.value = false
  }
}
</script>

<style scoped>
.settings-container {
  max-width: 800px;
  margin: 0 auto;
}

.settings-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-demo {
  margin: 16px 0;
}
</style>