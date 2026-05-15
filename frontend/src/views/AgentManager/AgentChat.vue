<template>
  <div class="agent-chat">
    <div class="chat-history">
      <div
        v-for="(msg, idx) in messages"
        :key="msg.timestamp + idx"
        :class="['chat-msg', msg.role, { prologue: msg.isPrologue }]"
      >
        <div class="msg-content">
          <template v-if="msg.isPrologue">
            <el-icon style="margin-right: 4px;"><ChatLineRound /></el-icon>
            <span>{{ msg.content }}</span>
          </template>
          <template v-else>
            {{ msg.content }}
          </template>
        </div>
      </div>
      <!-- AI思考中loading -->
      <div v-if="loading" class="chat-msg assistant loading-msg">
        <div class="msg-content">
          <el-icon class="loading-spin" style="margin-right: 4px;"><Loading /></el-icon>
          <span>AI正在思考...</span>
        </div>
      </div>
      <div v-if="messages.length === 0 && !loading" class="empty-tip">暂无对话内容</div>
    </div>
    <div class="chat-input">
      <el-input
        v-model="input"
        type="textarea"
        :rows="2"
        placeholder="请输入内容..."
        @keyup.enter.native="handleSend"
        :disabled="loading"
      />
      <el-button type="primary" @click="handleSend" :disabled="!input.trim() || loading">发送</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { chatWithAgent, getChatHistory } from '@/api/agent';
import { ChatLineRound, Loading } from '@element-plus/icons-vue';

const props = defineProps({
  agent: Object
});

const messages = ref([]);
const input = ref('');
const loading = ref(false);

// 加载聊天历史并插入开场白
const fetchHistory = async () => {
  if (props.agent && props.agent.agent_id) {
    const res = await getChatHistory(props.agent.agent_id);
    let history = [];
    // 兼容不同返回结构
    if (res && res.data && res.data.data && res.data.data.messages) {
      history = res.data.data.messages;
    } else if (res && res.data && res.data.messages) {
      history = res.data.messages;
    }
    // 如果历史为空且有开场白，插入开场白
    if ((!history || history.length === 0) && props.agent.prologue) {
      messages.value = [{
        role: 'assistant',
        content: props.agent.prologue,
        isPrologue: true,
        timestamp: new Date().toISOString()
      }];
    } else {
      messages.value = history || [];
    }
    input.value = '';
  } else {
    messages.value = [];
    input.value = '';
  }
};

const handleSend = async () => {
  if (!input.value.trim() || !props.agent || !props.agent.agent_id || loading.value) return;
  const userMsg = {
    role: 'user',
    content: input.value,
    timestamp: new Date().toISOString()
  };
  messages.value.push(userMsg);
  input.value = ''; // 立即清空输入框
  loading.value = true; // 显示AI思考中
  const res = await chatWithAgent(props.agent.agent_id, userMsg.content);
  let reply = '';
  if (res && res.data && res.data.data && res.data.data.message) {
    reply = res.data.data.message;
  } else if (res && res.data && res.data.message) {
    reply = res.data.message;
  }
  if (reply) {
    messages.value.push({
      role: 'assistant',
      content: reply,
      timestamp: new Date().toISOString()
    });
  }
  loading.value = false;
};

watch(() => props.agent, fetchHistory, { immediate: true });
onMounted(fetchHistory);
</script>

<style scoped>
.agent-chat {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.chat-history {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 16px;
}
.chat-msg {
  margin-bottom: 10px;
  display: flex;
}
.chat-msg.user .msg-content {
  background: #e6f7ff;
  align-self: flex-end;
}
.chat-msg.assistant .msg-content {
  background: #f0f0f0;
  align-self: flex-start;
}
.chat-msg.prologue .msg-content {
  background: #f5f7fa;
  color: #888;
  font-style: italic;
  display: flex;
  align-items: center;
}
.loading-msg .msg-content {
  color: #aaa;
  font-style: italic;
  display: flex;
  align-items: center;
}
.loading-spin {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  100% { transform: rotate(360deg); }
}
.msg-content {
  padding: 8px 14px;
  border-radius: 8px;
  max-width: 70%;
  word-break: break-all;
}
.empty-tip {
  color: #aaa;
  text-align: center;
  margin-top: 32px;
}
.chat-input {
  display: flex;
  gap: 8px;
}
</style>