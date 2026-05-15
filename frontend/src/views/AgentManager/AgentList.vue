<template>
  <div class="agent-list">
    <div
      v-for="agent in sortedAgents"
      :key="agent.agent_id"
      :class="['agent-item', { selected: agent.agent_id === selectedAgentId }]"
      @click="$emit('select', agent.agent_id)"
    >
      <el-avatar
        v-if="agent.photo"
        :src="getPhotoUrl(agent.photo)"
        size="small"
        class="agent-avatar"
      />
      <span class="agent-name">{{ agent.name }}</span>
    </div>
    <div v-if="!sortedAgents.length" class="empty-tip">暂无智能体，请先创建</div>
  </div>
</template>

<script setup>
import { defineProps, computed } from 'vue';

const props = defineProps({
  agents: Array,
  selectedAgentId: String
});

const sortedAgents = computed(() => {
  if (!props.agents) return [];
  // 按创建时间倒序排列
  return [...props.agents].sort((a, b) => new Date(b.create_time) - new Date(a.create_time));
});

const getPhotoUrl = (photo) => {
  if (!photo) return '';
  const filename = photo.split('/').pop();
  return `/api/chat/photo/${filename}`;
};
</script>

<style scoped>
.agent-list {
  flex: 1;
  overflow-y: auto;
}
.agent-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 4px;
  transition: background 0.2s;
}
.agent-item.selected {
  background: #e6f7ff;
}
.agent-avatar {
  margin-right: 8px;
}
.agent-name {
  flex: 1;
  font-size: 15px;
}
.empty-tip {
  color: #aaa;
  text-align: center;
  margin-top: 32px;
}
</style>