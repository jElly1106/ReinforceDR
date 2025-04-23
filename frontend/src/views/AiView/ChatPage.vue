<template>
    <div class="chat-container">
      <div class="chat-header">AI 医生助手</div>
      <div class="chat-body" ref="chatBody">
        <div v-for="(msg, index) in messages" :key="index" :class="['chat-msg', msg.from]">
          <div class="msg-bubble">{{ msg.text }}</div>
        </div>
      </div>
      <div class="chat-input">
        <el-input
          v-model="userInput"
          placeholder="请输入您的问题..."
          @keyup.enter="sendMessage"
          clearable
        />
        <el-button type="primary" @click="sendMessage">发送</el-button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, nextTick } from 'vue'
  
  const userInput = ref('')
  const messages = ref([
    { from: 'ai', text: '您好，我是 AI 医生，请描述您的症状或提问。' }
  ])
  
  const chatBody = ref(null)
  
  const sendMessage = async () => {
    if (!userInput.value.trim()) return
  
    // 显示用户消息
    messages.value.push({ from: 'user', text: userInput.value })
  
    // 模拟 AI 回复
    const userText = userInput.value
    userInput.value = ''
  
    await nextTick()
    chatBody.value.scrollTop = chatBody.value.scrollHeight
  
    setTimeout(() => {
      messages.value.push({ from: 'ai', text: `收到：${userText}，我会为您分析，请稍等...` })
      nextTick(() => {
        chatBody.value.scrollTop = chatBody.value.scrollHeight
      })
    }, 800)
  }
  
  onMounted(() => {
    const stored = localStorage.getItem('userSymptoms')
    if (stored) {
      const { name, age, symptoms } = JSON.parse(stored)
      messages.value.push({
        from: 'user',
        text: `患者姓名：${name}，年龄：${age}，症状描述：${symptoms}`
      })
      messages.value.push({
        from: 'ai',
        text: '好的，以下是我对您的症状的初步分析：...'
      })
    }
  })
  </script>
  
  <style scoped>
  .chat-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
  }
  .chat-header {
    background: #66003d;
    color: white;
    padding: 16px;
    font-size: 18px;
    font-weight: bold;
  }
  .chat-body {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
    background: #f5f5f5;
  }
  .chat-msg {
    margin-bottom: 12px;
    display: flex;
  }
  .chat-msg.user {
    justify-content: flex-end;
  }
  .chat-msg.ai {
    justify-content: flex-start;
  }
  .msg-bubble {
    max-width: 60%;
    padding: 12px;
    border-radius: 10px;
    background-color: #e6e6e6;
  }
  .chat-msg.user .msg-bubble {
    background-color: #66003d;
    color: white;
  }
  .chat-input {
    display: flex;
    padding: 12px;
    border-top: 1px solid #ddd;
    background: white;
    gap: 8px;
  }
  </style>
  