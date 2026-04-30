# Product Context

## Problem Statement
Linux users, particularly gamers on Arch/Hyprland/KdePlasma, lack a robust, integrated screen translation tool that handles context awareness well. Existing solutions often fail to group related text (breaking sentences) or lack advanced correction capabilities for stylized game fonts.

## Solution
A Python-based desktop application that leverages modern OCR and AI technologies to provide real-time or on-demand screen translation. It distinguishes itself with:
1. **Context Awareness**: Smart clustering of text blocks to preserve sentence meaning.
2. **Modular Architecture**: Users can choose their preferred engines for OCR and Translation.
3. **Wayland Native**: Designed with Hyprland in mind, handling the specific challenges of Wayland screen capturing and overlaying.

## User Experience Goals
- **"It just works"**: Minimal setup for basic functionality.
- **High Customizability**: Power users can tweak every aspect (backends, API keys, overlay styles).
- **Modern UI**: A visually appealing settings menu that fits a modern desktop aesthetic.
- **Low Latency**: Optimized pipeline for quick translations during gameplay.
