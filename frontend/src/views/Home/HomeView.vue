<template>
    <div class="main-container">
        <div class="main-content">
            <div class="left-container">
                <div class="left-content">
                    <div class="info-container">
                        <div class="info">
                            <img src="@/assets/staticIcon/Logo1.svg" class="logo" />
                            <div class="info-text">
                                <div style="font-size: 60px; font-weight: bold; text-align: left;">
                                    <span style="font-size: 60px; font-weight: bold; color: #630A45;">DR Prediction</span> Aid Platform
                                </div>
                                <div
                                    style="margin-top: 10px; color: #9E9E9E; font-size: 18px; text-align: left; font-weight: bold;">
                                    Provide convenient functions for predicting, and managing DR diagnosis and treatment.
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="function-container">
                        <div class="function-top" @click="clickFunction('modelpredict')">
                            <div class="function1-content">
                                <div class="function1-icon"
                                    style="height: 100%; aspect-ratio: 1; border-radius: 50%; background-color: #474747;">
                                    <img src="@/assets/staticIcon/home-prediction.svg" style="height: 100%;">
                                </div>
                                <div class="function1-text">
                                    <div style="font-size: 50px; font-weight: bold; text-align: left;">
                                        Model Prediction
                                    </div>
                                    <div class="function1-subtext">
                                        img and img_pos models are supported
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="function-bottom">
                            <div class="function2" @click="clickFunction('ai')">
                                <div class="function2-title">
                                    <div class="function2-icon">
                                        <img src="@/assets/staticIcon/home-test.svg" style="height: 100%;">
                                    </div>
                                    <div class="function2-name">
                                        Consultation
                                    </div>
                                </div>
                                <div class="function2-subtext">
                                    Ai Consult
                                </div>
                            </div>
                            <div class="function2" @click="clickFunction('modelmanage')">
                                <div class="function2-title">
                                    <div class="function2-icon">
                                        <img src="@/assets/staticIcon/home-manage.svg" style="height: 100%;">
                                    </div>
                                    <div class="function2-name">
                                        History
                                    </div>
                                </div>
                                <div class="function2-subtext">
                                    Manage your predict history
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
// import { ref } from 'vue';
import { useRouter } from 'vue-router';
const router = useRouter();

// //文档数据示例
// const documents = ref([
//     { 
//         title: "Glossary", 
//         subtitles: ["Key Concepts in Beamforming", "Beam Prediction Techniques"], 
//         link: "/help-pages/glossary.html" 
//     },
//     { 
//         title: "Dataset Upload for Training", 
//         subtitles: ["POS Training", "POS + IMG Training"], 
//         link: "/help-pages/TrainTestUp.html" 
//     },
//     { 
//         title: "Dataset Upload for Testing", 
//         subtitles: ["POS Testing", "POS + IMG Testing"], 
//         link: "/help-pages/TrainTestUp.html" 
//     },
//     { 
//         title: "Dataset Upload for Prediction", 
//         subtitles: ["POS Prediction", "POS + IMG Prediction"], 
//         link: "/help-pages/PredictUp.html" 
//     },
//     { 
//         title: "Position-Aided Model Guide", 
//         subtitles: ["Data Preprocessing and Normalization", "Model Loading and Prediction"], 
//         link: "/help-pages/Position-Aided Prediction Model Usage Guide.html" 
//     },
//     { 
//         title: "Image&Position Model Guide", 
//         subtitles: ["Data Preprocessing and Normalization", "Model Loading and Prediction"], 
//         link: "/help-pages/Image and Position Assistance Prediction Model File Usage Guide.html" 
//     },
// ]);

const clickFunction = (func) => {
    const path = '/sum/' + func; // 拼接路径
    router.push(path);
}

</script>

<style scoped>
.main-container {
    height: 100%;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
}

.main-content {
    height: 98%;
    width: 97%;
    margin-bottom: 10px;
    border-radius: 20px;
    border: 1px solid #E5E5E5;
    display: flex;
    flex-direction: row;
}

.left-container {
    height: 100%;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.right-container {
    height: 100%;
    width: 25%;
    border-radius: 0 20px 20px 0;
    background-color: #FCFCFC;
    display: flex;
    flex-direction: column;
}

.left-content {
    height: 85.5%;
    width: 1200px;
}

.info-container {
    height: 20%;
    display: flex;
    align-items: center;
}

.info {
    height: 81%;
    width: 100%;
    display: flex;
    justify-self: start;
}

.logo {
    height: 100%;
}

.info-text {
    margin-left: 55px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.function-container {
    margin-top: 20px;
    height: calc(80% - 20px);
    display: flex;
    flex-direction: column;

}

.function-top {
    width: 100%;
    height: calc(50% - 15px);
    background-color: #F7F7F7;
    border-radius: 20px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
}

.function1-content {
    width: 80%;
    height: 60%;
    display: flex;
    justify-self: start;
}

.function1-text {
    margin-left: 55px;
    width: 67%;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.function1-subtext {
    width: 100%;
    margin-top: 10px;
    color: #9E9E9E;
    font-size: 25px;
    text-align: left;
    font-weight: bold;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    overflow: hidden;
    -webkit-line-clamp: 3;
}

.function-bottom {
    width: 100%;
    height: calc(50% - 15px);
    margin-top: 30px;
    display: flex;
    flex-direction: row;
    gap: 20px;
}

.function2 {
    height: 100%;
    width: calc((100% - 20px) / 2);
    background-color: #F7F7F7;
    border-radius: 20px;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    /* justify-content: center; */
    align-items: center;
}

.function2-title {
    width: 80%;
    height: 80px;
    display: flex;
    flex-direction: row;
    margin-top: 10%;
}

.function2-icon {
    height: 100%;
    aspect-ratio: 1;
    border-radius: 50%;
    background-color: #787FE6;
}

.function2-name {
    margin-left: 20px;
    font-size: 40px;
    font-weight: bold;
    text-align: left;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.function2-subtext {
    width: 80%;
    margin-top: 10%;
    color: #9E9E9E;
    font-size: 20px;
    text-align: left;
    font-weight: bold;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    overflow: hidden;
    -webkit-line-clamp: 3;
}

.document-container {
    width: 100%;
    height: calc(100% - 90px);
    display: flex;
    justify-content: center;
}

.document-content {
    width: 90%;
    height: 100%;
    overflow-y: auto;
    overflow-x: hidden;
    margin-top: 10px;
    display: flex;
    flex-direction: column;
}

.document {
    width: 95%;
    border-radius: 10px;
    background-color: white;
    /* border: #787FE6 solid 1px; */
    margin-bottom: 20px;
    text-align: left;
}

.document-content::-webkit-scrollbar {
    width: 8px;
    /* 设置滚动条宽度 */
}

.document-content::-webkit-scrollbar-track {
    background: none;
}

.document-content::-webkit-scrollbar-thumb {
    background: #c9c9c9;
    /* 滚动条手柄颜色 */
    border-radius: 50vw;
}

.document-content::-webkit-scrollbar-thumb:hover {
    background: #8d8d8d;
    /* 滚动条手柄hover颜色 */
}
</style>