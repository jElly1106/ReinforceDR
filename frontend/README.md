# V2I_front

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### 接口请求示例
#### 查询参数传参方式，应对后端GET/DELETE
```javascript
let models = ref([])
const get_train_dataset_message = async () => {
    try {
    const response = await API.get('data/admin/get_train_dataset_message/', {
      params: {
        userid: userid
      }
    });
    models.value = response.data.data;
  } catch (error) {
    let errorMessage = ref('An unknown error occurred');
    if (error.response.data.message) {
      errorMessage = error.response.data.message;
    }
    ElMessage.error(errorMessage.value);
  }
}
```
#### 请求体传参方式，应对后端POST/PATCH/PUT
##### json构建请求体传参方式，无法文件传输

```javascript

const reviewDataset = async (model) => {
    try {
        const response = await API.patch('/data/admin/review_train_dataset/', {
        "userid": userid,
        "dataset_id": model.dataset_id,
        "is_qualified": value.value == 'approved' ? true : false,
        "rejection_reason": rejectedReason.value
        });
        ElMessage.success(response.data.message);
    } catch (error) {
        let errorMessage = ref('An unknown error occurred');
        if (error.response.data.message) {
          errorMessage = error.response.data.message;
        }
        ElMessage.error(errorMessage.value);
    }
}
```

##### FormData构建请求体传参方式，可以文件传输
```javascript

//谁写完了谁补充
```