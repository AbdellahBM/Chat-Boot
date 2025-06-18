import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LandingPageComponent } from './landing-page.component';
import { ChatbotComponent } from './chatbot/chatbot.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, LandingPageComponent, ChatbotComponent],
  template: `
    <app-landing-page *ngIf="!showChat" (startChat)="showChat = true"></app-landing-page>
    <app-chatbot *ngIf="showChat"></app-chatbot>
  `
})
export class AppComponent {
  showChat = false;
} 