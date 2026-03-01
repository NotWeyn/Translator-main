# Implementation Plan - Overlay Masking Fix

## Goal Description
Resolve the Hyprland overlay transparency and click-through issues by applying a window mask (`setMask`). This will restrict the window's effective surface to only the areas containing text, allowing the underlying applications to be seen and interacted with in the empty spaces.

## User Review Required
> [!NOTE]
> This approach relies on Qt's `setMask` function, which shapes the window. This should bypass Hyprland's blurring of transparent areas (since those areas won't exist) and allow clicks to pass through the empty space.

## Proposed Changes

### UI Component
#### [MODIFY] [src/ui/overlay.py](file:///home/notweyn/Programing/src/ui/overlay.py)
- **Refactor**: Extract the logic for calculating text block rectangles and font sizes from `paintEvent` into a new helper method `calculate_layout`.
- **Masking**: Implement `update_mask` method that:
    1. Calls `calculate_layout` to get the rectangles for all text blocks.
    2. Creates a `QRegion` combining these rectangles.
    3. Calls `self.setMask(region)` to shape the window.
- **Integration**: Call `update_mask` inside `set_text_blocks` to update the shape whenever text changes.

## Verification Plan

### Manual Verification
- **Transparency**:
    1. Enable Hyprland Mode.
    2. Trigger translation.
    3. Verify that the background is NOT blurred and is clearly visible in the spaces between text.
- **Click-Through**:
    1. Try to click on an application in the empty space between translated text blocks.
    2. Verify the click reaches the background app.
