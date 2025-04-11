<template>
  <div class="auth-container">
    <div class="auth-card" :class="{ 'animating': isAnimating, 'flipped': isFlipped }">
      <!-- 登录卡片 -->
      <div class="card-front">
        <div class="card-content">
          <div class="card-left">
            <h2>Hello, Welcome!</h2>
            <p>Don't have an account?</p>
            <button class="register-btn" @click="startAnimation">Register</button>
          </div>
          <div class="card-right">
            <h2>Login</h2>
            <div class="form-group">
              <input 
                type="email" 
                id="email" 
                v-model="loginForm.email" 
                placeholder="Email"
                required
              >
              <span class="input-icon">
                <i class="el-icon-message"></i>
              </span>
            </div>
            <div class="form-group">
              <input 
                type="password" 
                id="password" 
                v-model="loginForm.password" 
                placeholder="Password"
                required
              >
              <span class="input-icon">
                <i class="el-icon-lock"></i>
              </span>
            </div>
            <div class="forgot-password">
              <a href="#">Forgot password?</a>
            </div>
            <div class="error-message" v-if="loginError">{{ loginError }}</div>
            <button class="login-submit-btn" @click="handleLogin" :disabled="loginLoading">
              {{ loginLoading ? '登录中...' : 'Login' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- 注册卡片 -->
      <div class="card-back">
        <div class="card-content">
          <div class="card-left">
            <h2>Welcome Back!</h2>
            <p>Already have an account?</p>
            <button class="login-btn" @click="flipBack">Login</button>
          </div>
          <div class="card-right">
            <h2>Registration</h2>
            <div class="form-group">
              <input
                type="text"
                id="nickname"
                v-model="registerForm.nickname"
                placeholder="Username"
              />
              <span class="input-icon">
                <i class="el-icon-user"></i>
              </span>
            </div>
            <div class="form-group">
              <input
                type="email"
                id="register-email"
                v-model="registerForm.email"
                placeholder="Email"
              />
              <span class="input-icon">
                <i class="el-icon-message"></i>
              </span>
            </div>
            <div class="form-group captcha-group">
              <div class="captcha-input">
                <input
                  type="text"
                  id="captcha"
                  v-model="registerForm.captcha"
                  placeholder="Verification Code"
                />
                <button
                  class="captcha-btn"
                  @click="getCaptcha()"
                  :disabled="isButtonDisabled"
                >
                  {{ buttonText }}
                </button>
              </div>
            </div>
            <div class="form-group">
              <input
                type="password"
                id="register-password"
                v-model="registerForm.password"
                placeholder="Password"
              />
              <span class="input-icon">
                <i class="el-icon-lock"></i>
              </span>
            </div>
            <div class="form-group">
              <input
                type="password"
                id="confirm-password"
                v-model="confirmPassword"
                placeholder="Confirm Password"
              />
              <span class="input-icon">
                <i class="el-icon-lock"></i>
              </span>
            </div>
            <div class="error-message" v-if="registerError">{{ registerError }}</div>
            <button class="register-submit-btn" @click="handleRegister" :disabled="registerLoading">
              {{ registerLoading ? '注册中...' : 'Register' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Axios from "@/utils/axios.js";
import { isEmail } from "validator";

export default {
  name: 'AuthCard',
  data() {
    return {
      isAnimating: false,
      isFlipped: false,
      
      // 登录表单
      loginForm: {
        email: '',
        password: ''
      },
      loginError: '',
      loginLoading: false,
      
      // 注册表单
      registerForm: {
        email: "",
        nickname: "",
        password: "",
        captcha: "",
        captcha_id: "",
      },
      confirmPassword: "",
      registerError: "",
      registerLoading: false,
      
      // 验证码
      countdown: 60,
      isButtonDisabled: false,
      buttonText: "Get Code",
      timer: null,
    };
  },
  created() {
    const savedCountdown = localStorage.getItem("countdown");
    if (savedCountdown) {
      this.countdown = parseInt(savedCountdown);
      if (this.countdown > 0) {
        this.startCountdown();
      }
    }
  },
  methods: {
    // 动画控制
    startAnimation() {
      this.isAnimating = true;
      setTimeout(() => {
        this.isFlipped = true;
        setTimeout(() => {
          this.isAnimating = false;
        }, 800); // 与CSS动画时间匹配
      }, 500);
    },
    flipBack() {
      this.isAnimating = true;
      setTimeout(() => {
        this.isFlipped = false;
        setTimeout(() => {
          this.isAnimating = false;
        }, 800); // 与CSS动画时间匹配
      }, 500);
    },
    
    // 登录处理
    async handleLogin() {
      // 表单验证
      if (!this.loginForm.email || !this.loginForm.password) {
        this.loginError = '请填写完整的登录信息';
        return;
      }

      this.loginLoading = true;
      this.loginError = '';

      try {
        const response = await Axios.post('/user/login', this.loginForm);
        
        // 登录成功，保存token和用户信息
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('userId', response.data.user_id);
        
        // 提示登录成功
        this.$message.success('登录成功');
        
        // 跳转到首页或其他页面
        this.$router.push('/');
      } catch (error) {
        // 处理登录失败
        if (error.response && error.response.data) {
          this.loginError = error.response.data.error || '登录失败，请检查邮箱和密码';
        } else {
          this.loginError = '登录失败，请稍后再试';
        }
      } finally {
        this.loginLoading = false;
      }
    },
    
    // 注册处理
    async handleRegister() {
      // 表单验证
      if (!this.registerForm.email || !this.registerForm.nickname || 
          !this.registerForm.password || !this.confirmPassword || !this.registerForm.captcha) {
        this.registerError = '请填写完整的注册信息';
        return;
      }

      if (this.registerForm.password !== this.confirmPassword) {
        this.registerError = '两次输入的密码不一致';
        return;
      }
      
      if (!this.registerForm.captcha_id) {
        this.registerError = '请先获取验证码';
        return;
      }

      this.registerLoading = true;
      this.registerError = '';

      try {
        const req = {
          email: this.registerForm.email,
          nickname: this.registerForm.nickname,
          password: this.registerForm.password,
          captcha: this.registerForm.captcha,
          captcha_id: this.registerForm.captcha_id,
        };
        
        await Axios.post("/user/register", req);
        
        this.$message.success("注册成功");
        
        // 注册成功后翻转回登录页
        this.flipBack();
        
        // 清空注册表单
        this.registerForm = {
          email: "",
          nickname: "",
          password: "",
          captcha: "",
          captcha_id: "",
        };
        this.confirmPassword = "";
      } catch (error) {
        console.error('注册错误:', error);
        let errorMessage = "网络异常，注册失败";
        
        if (error && error.response && error.response.data) {
          errorMessage = error.response.data.error || errorMessage;
        }
        
        this.registerError = errorMessage;
      } finally {
        this.registerLoading = false;
      }
    },
    
    // 获取验证码
    async getCaptcha() {
      if (this.registerForm.email.trim().length == 0) {
        this.registerError = "邮箱未填写";
        return;
      }
      if (!isEmail(this.registerForm.email)) {
        this.registerError = "邮箱格式错误";
        return;
      }
      
      try {
        const res = await Axios.post("/user/send-captcha", {
          email: this.registerForm.email
        });
        
        this.$message.success("验证码已发送至邮箱");
        if (res && res.data && res.data.captcha_id) {
          this.registerForm.captcha_id = res.data.captcha_id;
        }
        this.startCountdown();
      } catch (error) {
        console.error('验证码发送错误:', error);
        
        let errorMessage = "网络异常，验证码发送失败";
        
        if (error && error.response && error.response.data) {
          errorMessage = error.response.data.error || errorMessage;
        }
        
        this.registerError = errorMessage;
      }
    },
    
    // 验证码倒计时
    startCountdown() {
      this.isButtonDisabled = true;
      this.timer = setInterval(() => {
        if (this.countdown > 0) {
          this.countdown--;
          this.buttonText = `${this.countdown}s`; // 从"秒后重发"改为"s"
          localStorage.setItem("countdown", this.countdown);
        } else {
          this.clearCountdown();
        }
      }, 1000);
    },
    clearCountdown() {
      clearInterval(this.timer);
      this.isButtonDisabled = false;
      this.countdown = 60;
      this.buttonText = "获取验证码";
      localStorage.removeItem("countdown");
    },
  },
    beforeUnmount() {
      if (this.timer) {
        clearInterval(this.timer);
    }
  }
};
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
  perspective: 1000px;
}

/* 统一动画时间和过渡效果 */
.auth-card {
  width: 800px;
  height: 500px;
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.8s ease-in-out; /* 统一翻转动画时间 */
  border-radius: 12px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

/* 统一正向和反向动画 */
.auth-card.animating .card-left {
  transition: width 0.8s ease-in-out;
  width: 100%;
  transition-delay: 0s; /* 确保宽度变化立即开始 */
}

.auth-card.animating.flipped .card-left {
  width: 40%;
  transition-delay: 0.5s; /* 延迟宽度变化，等待翻转完成一半 */
}

.auth-card.animating:not(.flipped) .card-left {
  width: 40%;
  transition-delay: 0.5s; /* 与上面保持一致 */
}

/* 确保登录按钮在动画过程中可点击 */
.login-btn {
  position: relative;
  z-index: 10;
  pointer-events: auto;
}

.auth-card.flipped {
  transform: rotateY(180deg);
}

.card-front, .card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 12px;
  overflow: hidden;
}

.card-back {
  transform: rotateY(180deg);
  z-index: 2; /* 增加注册卡片的层级，确保翻转后在最上层 */
}

.card-content {
  display: flex;
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.card-left {
  width: 40%;
  background-color: #7986cb;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px;
  text-align: center;
  transition: width 0.8s ease-in-out; /* 统一宽度变化时间 */
  z-index: 1;
}

/* 调整卡片右侧内容区域 */
.card-right {
  width: 60%;
  background-color: white;
  padding: 30px; /* 减小内边距 */
  display: flex;
  flex-direction: column;
  justify-content: center; /* 添加垂直居中 */
  transition: transform 0.8s ease-in-out; /* 统一过渡时间 */
  z-index: 0;
  overflow-y: auto;
  box-sizing: border-box; /* 确保padding不会增加宽度 */
  pointer-events: auto; /* 确保输入事件能够被捕获 */
}

/* 确保翻转后的表单可以接收输入 */
.auth-card.flipped .card-back .card-right,
.auth-card.flipped .card-back .card-left {
  pointer-events: auto;
  z-index: 3;
}

/* 确保未翻转时前面的表单可以接收输入 */
.auth-card:not(.flipped) .card-front .card-right,
.auth-card:not(.flipped) .card-front .card-left {
  pointer-events: auto;
  z-index: 3;
}

/* 修复注册表单滚动条问题 */
.card-back .card-right {
  overflow-y: hidden; /* 移除滚动条 */
  max-height: 100%; /* 确保高度不超过容器 */
}

/* 调整表单组间距，使注册表单更紧凑 */
.card-back .form-group {
  margin-bottom: 15px; /* 减小注册表单的间距 */
}

/* 调整输入框高度，使其更紧凑 */
.card-back input {
  padding: 10px 15px 10px 40px; /* 减小输入框高度 */
}

.auth-card.animating .card-right {
  transform: translateX(100%);
  transition: transform 0.8s ease-in-out;
  transition-delay: 0s;
}

.auth-card.animating.flipped .card-right {
  transform: translateX(0);
  transition-delay: 0.5s;
}

.auth-card.animating:not(.flipped) .card-right {
  transform: translateX(0);
  transition-delay: 0.5s;
}

h2 {
  margin-bottom: 20px;
  font-weight: 600;
  color: #333;
}

.card-left h2 {
  color: white;
  font-size: 28px;
  margin-bottom: 15px;
}

.card-left p {
  margin-bottom: 30px;
  font-size: 16px;
}

.login-btn, .register-btn {
  background-color: transparent;
  color: white;
  border: 2px solid white;
  padding: 10px 30px;
  border-radius: 30px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.login-btn:hover, .register-btn:hover {
  background-color: white;
  color: #7986cb;
}

.form-group {
  position: relative;
  margin-bottom: 20px;
  width: 100%;
}

input {
  width: 100%;
  padding: 12px 15px;
  padding-left: 40px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.3s;
  box-sizing: border-box; /* 确保padding不会增加宽度 */
}

input:focus {
  border-color: #7986cb;
  outline: none;
}

.input-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
}

.forgot-password {
  text-align: right;
  margin-bottom: 20px;
}

.forgot-password a {
  color: #7986cb;
  text-decoration: none;
}

/* 调整验证码输入框组 */
.captcha-group {
  margin-bottom: 20px;
  width: 100%;
}

.captcha-input {
  display: flex;
  gap: 10px;
  width: 100%;
}

.captcha-input input {
  flex: 1;
}

.captcha-btn {
  background-color: #7986cb;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0 10px; /* 减小内边距 */
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s;
  white-space: nowrap;
  min-width: 100px; /* 减小最小宽度 */
}

.captcha-btn:hover:not(:disabled) {
  background-color: #5c6bc0;
}

.captcha-btn:disabled {
  background-color: #b0bec5;
  cursor: not-allowed;
}

.login-submit-btn, .register-submit-btn {
  width: 100%;
  padding: 12px;
  background-color: #7986cb;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-bottom: 20px;
}

.login-submit-btn:hover, .register-submit-btn:hover {
  background-color: #5c6bc0;
}

.login-submit-btn:disabled, .register-submit-btn:disabled {
  background-color: #b0bec5;
  cursor: not-allowed;
}

.error-message {
  color: #f56c6c;
  margin-bottom: 15px;
  font-size: 14px;
}
</style>