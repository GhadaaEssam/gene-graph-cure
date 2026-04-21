// services/auth.api.js

export const registerUser = async (userData) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // بنعمل محاكاة إن الإيميل ده متسجل قبل كده
      if (userData.email === "test@university.edu") {
        reject(new Error("Email already exists."));
      } else {
        // لو كل حاجة تمام، بنرجع توكن وهمي وداتا اليوزر
        resolve({
          status: "success",
          token: "fake_jwt_token_12345",
          user: {
            name: userData.fullName,
            email: userData.email
          }
        });
      }
    }, 1500); // تأخير ثانية ونص عشان الـ Loading
  });
};
// services/auth.api.js

// الفانكشن دي بتعمل محاكاة لعملية تسجيل الدخول
export const loginUser = async (credentials) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // محاكاة لحالة الخطأ (لو الباسورد غلط مثلاً)
      if (credentials.email === "error@university.edu") {
        reject(new Error("Invalid email or password. Please try again."));
      } else {
        // حالة النجاح
        resolve({
          status: "success",
          token: "fake_jwt_token_98765", // توكن وهمي عشان الـ Dashboard تفتح
          user: {
            name: "Dr. Smith", // ده الاسم اللي هيظهر في الداشبورد
            email: credentials.email
          }
        });
      }
    }, 1500); // تأخير ثانية ونص للتحميل
  });
};