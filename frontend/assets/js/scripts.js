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
            const response = await fetch(`${BASE_URL}/users`);
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
    if (document.getElementById("usersTable")) loadUsers();

    // ------------------------------
    // Funções para Accounts
    // ------------------------------

    // Criar Conta
    const createAccountForm = document.getElementById("createAccountForm");
    if (createAccountForm) {
        createAccountForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const accountData = {
                user_id: document.getElementById("user_id").value,
                initial_balance: document.getElementById("initial_balance").value,
            };

            try {
                const response = await fetch(`${BASE_URL}/accounts`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(accountData),
                });
                const result = await response.json();
                alert(result.message || result.error);
                if (result.message) loadAccounts();
            } catch (error) {
                console.error("Erro ao criar conta:", error);
            }
        });
    }

    // Carregar Contas
    async function loadAccounts() {
        try {
            const response = await fetch(`${BASE_URL}/accounts`);
            if (response.ok) {
                const accounts = await response.json();
                const accountsTable = document.getElementById("accountsTable").querySelector("tbody");
                accountsTable.innerHTML = "";

                accounts.forEach((account) => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${account.account_id}</td>
                        <td>${account.user_id}</td>
                        <td>${account.balance}</td>
                    `;
                    accountsTable.appendChild(row);
                });
            } else {
                const errorResult = await response.json();
                alert(`Erro ao carregar contas: ${errorResult.error}`);
            }
        } catch (error) {
            console.error("Erro ao carregar contas:", error);
        }
    }
    if (document.getElementById("accountsTable")) loadAccounts();

    // ------------------------------
    // Funções para Transactions
    // ------------------------------

    // Realizar Transferência
    const transferFundsForm = document.getElementById("transferFundsForm");
    if (transferFundsForm) {
        transferFundsForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const transactionData = {
                from_account: document.getElementById("from_account").value,
                to_account: document.getElementById("to_account").value,
                amount: document.getElementById("amount").value,
            };

            try {
                const response = await fetch(`${BASE_URL}/transactions/transfer`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(transactionData),
                });
                const result = await response.json();
                alert(result.message || result.error);
                if (result.message) loadTransactions();
            } catch (error) {
                console.error("Erro ao realizar transferência:", error);
            }
        });
    }

    // Carregar Transações
    async function loadTransactions() {
        try {
            const response = await fetch(`${BASE_URL}/transactions`);
            if (response.ok) {
                const transactions = await response.json();
                const transactionsTable = document.getElementById("transactionsTable").querySelector("tbody");
                transactionsTable.innerHTML = "";

                transactions.forEach((transaction) => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${transaction.transaction_id}</td>
                        <td>${transaction.from_account}</td>
                        <td>${transaction.to_account}</td>
                        <td>${transaction.amount}</td>
                        <td>${transaction.transaction_date}</td>
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
    if (document.getElementById("transactionsTable")) loadTransactions();
});
