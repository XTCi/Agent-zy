<template>
  <el-drawer
    :model-value="true"
    title="智能体详情"
    size="400px"
    @close="$emit('close')"
  >
    <div class="agent-detail-header">
      <img :src="getPhotoUrl(agent.photo)" class="avatar" v-if="agent.photo" />
      <div class="info">
        <div class="name">{{ agent.name }}</div>
        <div class="desc">{{ agent.introduce }}</div>
      </div>
    </div>
    <el-button class="block-btn" type="primary" @click="editVisible = true" icon="el-icon-edit">编辑</el-button>
    <div class="knowledge-section">
      <el-divider>知识库</el-divider>
      <div class="knowledge-btn-center">
        <el-button type="info" @click="$emit('uploadKnowledge')">管理知识库</el-button>
      </div>
    </div>
    <el-divider />
    <el-button class="remove-btn" type="danger" @click="onRemove" plain>移除</el-button>

    <!-- 编辑弹窗 -->
    <AgentEditModal
      v-if="editVisible"
      :agent="agent"
      @close="editVisible = false"
      @updated="onUpdated"
    />
  </el-drawer>
</template>

<script setup>
import { ref } from 'vue'
import AgentEditModal from './AgentEditModal.vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { deleteAgent, getAgentDetail } from '@/api/agent'

const props = defineProps({ agent: Object })
const emit = defineEmits(['close', 'removed', 'updated', 'uploadKnowledge'])

const editVisible = ref(false)

function getPhotoUrl(photo) {
  if (!photo) return '';
  // 如果已经是完整url，直接返回
  if (/^https?:\/\//.test(photo)) return photo;
  // 如果是 /uploads/agents/xxx 这种，拼接API前缀
  if (photo.startsWith('/uploads/')) {
    const filename = photo.split('/').pop();
    return `/api/chat/photo/${filename}`;
  }
  return photo;
}

async function onRemove() {
  try {
    await ElMessageBox.confirm('确定要删除该智能体吗？此操作不可恢复。', '警告', { type: 'warning' })
    await deleteAgent(props.agent.agent_id)
    ElMessage.success('删除成功')
    emit('removed')
    emit('close')
  } catch (e) {}
}

async function onUpdated(updatedAgent) {
  emit('updated', updatedAgent)
  editVisible.value = false
}
</script>

<style scoped>
.agent-detail-header { display: flex; align-items: center; margin-bottom: 20px; }
.avatar { width: 80px; height: 80px; border-radius: 50%; margin-right: 16px; object-fit: cover; background: #f5f5f5; }
.info { flex: 1; }
.name { font-size: 20px; font-weight: bold; }
.desc { color: #888; margin-top: 4px; }
.block-btn { width: 100%; margin-bottom: 10px; }
.knowledge-section { margin: 24px 0 0 0; }
.knowledge-btn-center { display: flex; justify-content: center; }
.remove-btn { width: 100%; margin-top: 32px; }
</style>