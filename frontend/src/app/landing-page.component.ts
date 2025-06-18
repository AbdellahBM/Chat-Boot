import { Component, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-landing-page',
  standalone: true,
  templateUrl: './landing-page.component.html',
  styleUrls: ['./landing-page.component.css']
})
export class LandingPageComponent {
  @Output() startChat = new EventEmitter<void>();

  onStartChat() {
    this.startChat.emit();
  }
} 