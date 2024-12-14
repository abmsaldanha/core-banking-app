document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
 
    try {
        const response = await fetch("http://127.0.0.1:5000/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ email, password }),
        });
 
        if (response.ok) {
            alert("Login bem-sucedido!");
            window.location.href = "dashboard.html"; // Redireciona para a dashboard
        } else {
            document.getElementById("errorMessage").style.display = "block";
        }
    } catch (error) {
        console.error("Erro ao fazer login:", error);
        document.getElementById("errorMessage").style.display = "block";
    }
});