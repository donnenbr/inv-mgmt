import React from 'react';
import type {Meta, StoryObj} from '@storybook/react';

import {SearchInventory} from './SearchInventory';

const meta: Meta<typeof SearchInventory> = {
  component: SearchInventory,
};

export default meta;

type Story = StoryObj<typeof SearchInventory>;

export const Basic: Story = {args: {}};
