const BASE_URL = "http://127.0.0.1:5000";

 
document.addEventListener("DOMContentLoaded", () => {
    // ------------------------------
    // Funções para Users
    // ------------------------------
 
   // Criar Utilizador
const createUserForm = document.getElementById("createUserForm");
if (createUserForm) {
    createUserForm.addEventListener("submit", async (e) => {
        e.preventDefault();
 
        const userData = {
            name: document.getElementById("name").value,
            email: document.getElementById("email").value,
            password: document.getElementById("password").value,
            nif: document.getElementById("nif").value,
            birth_date: document.getElementById("birth_date").value,
            address: document.getElementById("address").value,
            phone: document.getElementById("phone").value,
        };
 
        try {
            const response = await fetch(`${BASE_URL}/users`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include", // Garante que os cookies de sessão são enviados
                body: JSON.stringify(userData),
            });
            const result = await response.json();
            alert(result.message || result.error);
            if (result.message) loadUsers();
        } catch (error) {
            console.error("Erro ao criar utilizador:", error);
        }
    });
}
 
   // Carregar Utilizadores
async function loadUsers() {
    try {
        const response = await fetch(`${BASE_URL}/users`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include", // Garante que os cookies de sessão são enviados
        });
 
        if (response.ok) {
            const users = await response.json();
            const usersTable = document.getElementById("usersTable").querySelector("tbody");
            usersTable.innerHTML = "";
 
            users.forEach((user) => {
                const row = document.createElement("tr");
                row.innerHTML = `
<td>${user.user_id}</td>
<td>${user.name}</td>
<td>${user.email}</td>
<td>${user.nif}</td>
                `;
                usersTable.appendChild(row);
            });
        } else {
            const errorResult = await response.json();
            alert(`Erro ao carregar utilizadores: ${errorResult.error}`);
        }
    } catch (error) {
        console.error("Erro ao carregar utilizadores:", error);
    }
}
 
    // ------------------------------
    // Funções para Transactions
    // ------------------------------
 
 // Realizar Transferência
const transferFundsForm = document.getElementById("transferFundsForm");
if (transferFundsForm) {
    transferFundsForm.addEventListener("submit", async (e) => {
        e.preventDefault();
 
        const transactionData = {
            to_iban: document.getElementById("to_iban").value,
            amount: document.getElementById("amount").value,
        };
 
        try {
            const response = await fetch(`${BASE_URL}/transactions`, {
                //mode: "no-cors",
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include", // Garante que os cookies de sessão são enviados
                body: JSON.stringify(transactionData),
            });
 
            if (response.ok) {
                alert("Transferência realizada com sucesso!");
                loadTransactions(); // Atualizar o histórico de transações
            } else {
                const error = await response.json();
                alert(error.error || "Erro ao realizar transferência.");
            }
        } catch (error) {
            console.error("Erro ao realizar transferência:", error);
        }
    });
}
 
    // Carregar Transações
async function loadTransactions() {
    try {
        const response = await fetch(`${BASE_URL}/transactions`, {
            //mode: "no-cors",
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include", // Garante que os cookies de sessão são enviados
        });
 
        if (response.ok) {
            const transactions = await response.json();
            const transactionsTable = document.getElementById("transactionsTable").querySelector("tbody");
            transactionsTable.innerHTML = "";
 
            transactions.forEach((transaction) => {
                const row = document.createElement("tr");
                row.innerHTML = `
<td>${transaction.transaction_id}</td>
<td>${transaction.to_iban}</td>
<td>€ ${transaction.amount.toFixed(2)}</td>
<td>${new Date(transaction.transaction_date).toLocaleString("pt-PT")}</td>
                `;
                transactionsTable.appendChild(row);
            });
        } else {
            const errorResult = await response.json();
            alert(`Erro ao carregar transações: ${errorResult.error}`);
        }
    } catch (error) {
        console.error("Erro ao carregar transações:", error);
    }
}
});