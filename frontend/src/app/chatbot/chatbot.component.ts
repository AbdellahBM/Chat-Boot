import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';     // Pour *ngIf, *ngFor, [ngClass]
import { FormsModule } from '@angular/forms';       // Pour [(ngModel)]

interface ChatMessage {
  from: 'user' | 'bot';
  text: string;
  timestamp?: Date;
}

interface ApiResponse {
  response: string;
  error?: string;
}

@Component({
  selector: 'app-chatbot',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css']
})
export class ChatbotComponent {
  userInput = '';
  showChat = false;
  messages: ChatMessage[] = [];
  isLoading = false;
  private readonly apiUrl = 'http://127.0.0.1:5001/api/chat';

  toggleChat() {
    this.showChat = !this.showChat;
  }

  sendMessage() {
    if (!this.userInput.trim() || this.isLoading) return;

    const userMessage: ChatMessage = {
      from: 'user',
      text: this.userInput,
      timestamp: new Date()
    };

    this.messages.push(userMessage);
    const currentInput = this.userInput;
    this.userInput = '';
    this.isLoading = true;

    fetch(this.apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: currentInput })
    })
    .then(res => {
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      return res.json();
    })
    .then((data: ApiResponse) => {
      const botMessage: ChatMessage = {
        from: 'bot',
        text: data.response,
        timestamp: new Date()
      };
      this.messages.push(botMessage);
    })
    .catch(error => {
      console.error('Error sending message:', error);
      const errorMessage: ChatMessage = {
        from: 'bot',
        text: 'Sorry, I encountered an error. Please try again later.',
        timestamp: new Date()
      };
      this.messages.push(errorMessage);
    })
    .finally(() => {
      this.isLoading = false;
    });
  }
}
