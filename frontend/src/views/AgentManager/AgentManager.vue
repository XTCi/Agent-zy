<template>
  <div class="agent-manager-outer">
    <div class="agent-manager-layout">
      <!-- 左侧：智能体列表 -->
      <div class="agent-sidebar">
        <el-button type="primary" @click="showCreateModal = true" class="create-btn">创建智能体</el-button>
        <AgentList
          :agents="agents"
          :selectedAgentId="selectedAgentId"
          @select="handleSelectAgent"
        />
      </div>
      <!-- 中间：对话区 -->
      <div class="agent-chat-area">
        <AgentChat :agent="currentAgent" :key="chatKey" />
      </div>
      <!-- 右侧：详情与操作 -->
      <div class="agent-detail-area">
        <el-button @click="clearHistory">清除上下文</el-button>
        <el-button @click="showDetailDrawer = true">详情</el-button>
        <AgentDetailDrawer
          v-if="showDetailDrawer"
          :agent="currentAgent"
          @close="showDetailDrawer = false"
          @updated="handleAgentUpdated"
          @uploadKnowledge="showUploadModal = true"
          @removed="handleAgentRemoved"
        />
      </div>
      <!-- 弹窗区 -->
      <AgentCreateModal v-if="showCreateModal" @close="showCreateModal = false" @created="fetchAgents" />
      <KnowledgeUploadModal v-if="showUploadModal" @close="showUploadModal = false" :agentId="selectedAgentId" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import AgentList from './AgentList.vue';
import AgentCreateModal from './AgentCreateModal.vue';
import AgentChat from './AgentChat.vue';
import AgentDetailDrawer from './AgentDetailDrawer.vue';
import KnowledgeUploadModal from './KnowledgeUploadModal.vue';
import { getAgentList, deleteAgent, clearChatHistory } from '@/api/agent';

const agents = ref([]);
const selectedAgentId = ref(null);
const showCreateModal = ref(false);
const showDetailDrawer = ref(false);
const showUploadModal = ref(false);
const chatKey = ref(0); // 用于强制刷新AgentChat
const router = useRouter();

const currentAgent = computed(() => agents.value.find(a => a.agent_id === selectedAgentId.value));

const fetchAgents = async () => {
  const res = await getAgentList();
  if (res && res.data && res.data.data && res.data.data.agents) {
    agents.value = res.data.data.agents;
    if (!selectedAgentId.value && agents.value.length > 0) {
      selectedAgentId.value = agents.value[0].agent_id;
    }
  }
};

const handleSelectAgent = (agentId) => {
  selectedAgentId.value = agentId;
};

const handleAgentUpdated = async (updatedAgent) => {
  await fetchAgents();
  if (updatedAgent && updatedAgent.agent_id) {
    selectedAgentId.value = updatedAgent.agent_id;
    // 强制刷新聊天区和详情
    chatKey.value += 1;
    // 关闭详情抽屉（可选）
    showDetailDrawer.value = false;
    // 等待DOM更新后再打开详情，确保currentAgent是最新的
    await nextTick();
    showDetailDrawer.value = true;
  }
};

const handleAgentRemoved = async () => {
  await fetchAgents();
  if (agents.value.length > 0) {
    selectedAgentId.value = agents.value[0].agent_id;
  } else {
    selectedAgentId.value = null;
  }
  chatKey.value += 1;
};

const clearHistory = async () => {
  if (!currentAgent.value) return;
  await clearChatHistory(currentAgent.value.agent_id);
  chatKey.value += 1;
};

onMounted(() => {
  const token = localStorage.getItem('token');
  if (!token) {
    router.push('/login');
    return;
  }
  fetchAgents();
});
</script>

<style scoped>
.agent-manager-outer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
  overflow: hidden;
  z-index: 1;
}
.agent-manager-layout {
  display: flex;
  width: 100%;
  max-width: 1200px;
  min-width: 900px;
  min-height: 80vh;
  background: #f5f7fa;
  box-shadow: 0 4px 24px rgba(0,0,0,0.06);
  border-radius: 16px;
  justify-content: center;
  align-items: stretch;
}
.agent-sidebar {
  width: 220px;
  background: #f7f8fa;
  padding: 16px 8px;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  border-top-left-radius: 16px;
  border-bottom-left-radius: 16px;
}
.create-btn {
  margin-bottom: 16px;
}
.agent-chat-area {
  flex: 1 1 0;
  max-width: 800px;
  min-width: 350px;
  padding: 24px 32px;
  background: #fff;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  margin: 0 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
  border-radius: 10px;
}
.agent-detail-area {
  width: 220px;
  background: #fafbfc;
  padding: 16px;
  border-left: 1px solid #eee;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  overflow-y: auto;
  border-top-right-radius: 16px;
  border-bottom-right-radius: 16px;
}
@media (max-width: 1200px) {
  .agent-manager-layout {
    max-width: 100vw;
    min-width: 0;
    border-radius: 0;
  }
  .agent-sidebar, .agent-detail-area {
    width: 120px;
    padding: 8px 2px;
    border-radius: 0;
  }
  .agent-chat-area {
    max-width: 100vw;
    min-width: 0;
    padding: 12px 4px;
    margin: 0 2px;
    border-radius: 0;
  }
}
@media (max-width: 800px) {
  .agent-manager-layout {
    flex-direction: column;
    align-items: stretch;
    min-width: 0;
    max-width: 100vw;
  }
  .agent-sidebar, .agent-detail-area {
    width: 100%;
    border-right: none;
    border-left: none;
    border-radius: 0;
  }
  .agent-chat-area {
    margin: 0;
    border-radius: 0;
  }
}
</style>