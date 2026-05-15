<template>
  <div class="chat-container">
    <div class="chat-messages" ref="messagesContainer">
      <div v-for="(message, index) in messages" :key="index" :class="['message', message.role]">
        <el-avatar :icon="message.role === 'user' ? UserFilled : Service" />
        <div class="message-content">{{ message.content }}</div>
      </div>
    </div>
    <div class="chat-input">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="3"
        placeholder="请输入您的问题..."
        @keyup.enter.native="sendMessage"
      />
      <el-button type="primary" @click="sendMessage" :loading="loading">发送</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { UserFilled, Service } from '@element-plus/icons-vue'
import { chatWithAgent } from '../api'
import { ElMessage } from 'element-plus'

const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

  const userMessage = inputMessage.value
  messages.value.push({ role: 'user', content: userMessage })
  inputMessage.value = ''
  loading.value = true

  try {
    const response = await chatWithAgent(userMessage)
    if (response.data.code === 1) {
      messages.value.push({ role: 'assistant', content: response.data.data.msg.output })
    } else {
      ElMessage.error(response.data.message || '发送消息失败')
    }
    await scrollToBottom()
  } catch (error) {
    ElMessage.error('发送消息失败，请重试')
    console.error('Error:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  messages.value = [
    { role: 'assistant', content: '你好！我是你的AI助手，有什么可以帮你的吗？' }
  ]
})
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: white;
  border-radius: 8px;
  margin-bottom: 20px;
}

.message {
  display: flex;
  align-items: flex-start;
  margin-bottom: 20px;
  gap: 12px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-content {
  background: #f4f4f5;
  padding: 12px;
  border-radius: 8px;
  max-width: 70%;
}

.message.user .message-content {
  background: #95ec69;
}

.chat-input {
  display: flex;
  gap: 12px;
}

.chat-input .el-textarea {
  flex: 1;
}
</style>