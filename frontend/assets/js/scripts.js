const BASE_URL = "http://127.0.0.1:5000";

// Função para obter o token JWT
function getToken() {
    return localStorage.getItem("token");
}

// Função para redirecionar se não autenticado
function checkAuth() {
    const token = getToken();
    if (!token) {
        alert("Sessão expirada ou inválida. Faça login novamente.");
        window.location.href = "login.html";
    }
}

// Login
document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch(`${BASE_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });

        const result = await response.json();
        if (response.ok) {
            localStorage.setItem("token", result.token); // Guarda o token JWT
            alert("Login bem-sucedido!");
            window.location.href = "dashboard.html";
        } else {
            alert(result.error || "Erro ao fazer login.");
        }
    } catch (error) {
        console.error("Erro ao fazer login:", error);
    }
});

// Logout
document.getElementById("logoutButton").addEventListener("click", async () => {
    const token = localStorage.getItem("token");
 
    if (token) {
        try {
            await fetch("http://127.0.0.1:5000/logout", {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });
        } catch (error) {
            console.error("Erro ao fazer logout:", error);
        }
    }
 
    // Remove o token localmente e redireciona
    localStorage.removeItem("token");
    window.location.href = "login.html";
});

// Carregar Utilizadores (Protegido)
async function loadUsers() {
    checkAuth(); // Verifica autenticação
    const token = getToken();

    try {
        const response = await fetch(`${BASE_URL}/users`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`, // Envia o token no cabeçalho
            },
        });

        if (response.ok) {
            const users = await response.json();
            const usersTable = document.getElementById("usersTable")?.querySelector("tbody");
            if (usersTable) {
                usersTable.innerHTML = ""; // Limpa a tabela

                users.forEach((user) => {
                    const row = `
<tr>
<td>${user.user_id}</td>
<td>${user.name}</td>
<td>${user.email}</td>
<td>${user.nif}</td>
</tr>
                    `;
                    usersTable.innerHTML += row;
                });
            }
        } else {
            alert("Erro ao carregar utilizadores. Faça login novamente.");
            window.location.href = "login.html";
        }
    } catch (error) {
        console.error("Erro ao carregar utilizadores:", error);
    }
}

// Realizar Transferência (Protegido)
document.getElementById("transferFundsForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    checkAuth(); // Verifica autenticação
    const token = getToken();

    const transactionData = {
        to_iban: document.getElementById("to_iban").value,
        amount: document.getElementById("amount").value,
    };

    const transferButton = document.getElementById("transferButton");
    transferButton.disabled = true; // Desabilita o botão enquanto processa

    try {
        const response = await fetch(`${BASE_URL}/transactions`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`, // Envia o token JWT
            },
            body: JSON.stringify(transactionData),
        });

        const result = await response.json();
        if (response.ok) {
            alert("Transferência realizada com sucesso!");
            loadTransactions(); // Atualiza a lista de transações
        } else {
            alert(result.error || "Erro ao realizar transferência.");
        }
    } catch (error) {
        console.error("Erro ao realizar transferência:", error);
    } finally {
        transferButton.disabled = false; // Reabilita o botão após a requisição
    }
});

// Carregar Transações (Protegido)
async function loadTransactions() {
    checkAuth(); // Verifica autenticação
    const token = getToken();

    try {
        const response = await fetch(`${BASE_URL}/transactions`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`, // Envia o token JWT
            },
        });

        if (response.ok) {
            const transactions = await response.json();
            const transactionsTable = document.getElementById("transactionsTable")?.querySelector("tbody");
            if (transactionsTable) {
                transactionsTable.innerHTML = ""; // Limpa a tabela

                transactions.forEach((transaction) => {
                    const row = `
<tr>
<td>${transaction.transaction_id}</td>
<td>${transaction.to_iban}</td>
<td>€ ${transaction.amount.toFixed(2)}</td>
<td>${new Date(transaction.transaction_date).toLocaleString("pt-PT")}</td>
</tr>
                    `;
                    transactionsTable.innerHTML += row;
                });
            }
        } else {
            alert("Erro ao carregar transações. Faça login novamente.");
            window.location.href = "login.html";
        }
    } catch (error) {
        console.error("Erro ao carregar transações:", error);
    }
}


// Inicializar Página
document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("usersTable")) loadUsers();
    if (document.getElementById("transactionsTable")) loadTransactions();
});
