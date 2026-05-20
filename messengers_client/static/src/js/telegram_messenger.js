/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class TelegramMessenger extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.messagesRef = useRef("messages");

        this.state = useState({
            chats: [],
            messages: [],
            selectedChat: null,
            messageInput: "",
            searchQuery: "",
        });

        onWillStart(async () => {
            await this.loadChats();
        });
    }

    async loadChats() {
        try {
            const chats = await this.orm.searchRead(
                "telegram.chat",
                [],
                ["name", "username", "chat_id", "unread_count"],
                { order: "id desc" }
            );
            this.state.chats = chats || [];
        } catch (error) {
            console.error("Error loading chats:", error);
            this.state.chats = [];
        }
    }

    async loadMessages(chatId) {
        try {
            const messages = await this.orm.searchRead(
                "telegram.message",
                [["chat_id", "=", chatId]],
                ["content", "date", "is_incoming", "is_read", "sender_name"],
                { order: "date asc" }
            );
            this.state.messages = messages;

            // Позначити як прочитані
            await this.orm.call("telegram.chat", "mark_as_read", [[chatId]]);
            await this.loadChats();

            // Прокрутити вниз
            setTimeout(() => {
                if (this.messagesRef.el) {
                    this.messagesRef.el.scrollTop = this.messagesRef.el.scrollHeight;
                }
            }, 100);
        } catch (error) {
            console.error("Error loading messages:", error);
            this.notification.add("Помилка завантаження повідомлень", { type: "danger" });
        }
    }

    async selectChat(chat) {
        this.state.selectedChat = chat;
        await this.loadMessages(chat.id);
    }

    async sendMessage() {
        if (!this.state.messageInput.trim() || !this.state.selectedChat) {
            return;
        }

        try {
            // Викликаємо метод відправки через Telegram API
            await this.orm.call(
                "telegram.chat",
                "send_telegram_message",
                [[this.state.selectedChat.id], this.state.messageInput]
            );

            this.state.messageInput = "";
            await this.loadMessages(this.state.selectedChat.id);

            this.notification.add("Повідомлення відправлено", { type: "success" });
        } catch (error) {
            console.error("Error sending message:", error);
            this.notification.add("Помилка відправки повідомлення", { type: "danger" });
        }
    }

    onMessageKeydown(ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            this.sendMessage();
        }
    }

    getInitials(name) {
        if (!name) return "?";
        const parts = name.split(" ");
        if (parts.length >= 2) {
            return (parts[0][0] + parts[1][0]).toUpperCase();
        }
        return name.substring(0, 2).toUpperCase();
    }

    formatTime(datetime) {
        if (!datetime) return "";
        const date = new Date(datetime);
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const messageDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

        if (messageDate.getTime() === today.getTime()) {
            return date.toLocaleTimeString("uk-UA", { hour: "2-digit", minute: "2-digit" });
        } else {
            return date.toLocaleDateString("uk-UA", { day: "2-digit", month: "2-digit" });
        }
    }

    getLastMessage(chat) {
        // Показуємо повідомлення з state.messages якщо чат вибраний
        if (this.state.selectedChat && this.state.selectedChat.id === chat.id && this.state.messages.length > 0) {
            const lastMsg = this.state.messages[this.state.messages.length - 1];
            return lastMsg.content || "";
        }
        return "Немає повідомлень";
    }

    getLastMessageTime(chat) {
        if (this.state.selectedChat && this.state.selectedChat.id === chat.id && this.state.messages.length > 0) {
            const lastMsg = this.state.messages[this.state.messages.length - 1];
            return this.formatTime(lastMsg.date);
        }
        return "";
    }

    get filteredChats() {
        if (!this.state.searchQuery) {
            return this.state.chats;
        }
        const query = this.state.searchQuery.toLowerCase();
        return this.state.chats.filter(chat =>
            chat.name.toLowerCase().includes(query) ||
            (chat.username && chat.username.toLowerCase().includes(query))
        );
    }
}

TelegramMessenger.template = "messengers_client.TelegramMessenger";

registry.category("actions").add("telegram_messenger", TelegramMessenger);