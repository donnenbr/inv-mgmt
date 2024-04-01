import React from 'react';
import type {Meta, StoryObj} from '@storybook/react';

import {LocateVial} from './LocateVial';

const meta: Meta<typeof LocateVial> = {
  component: LocateVial,
};

export default meta;

type Story = StoryObj<typeof LocateVial>;

export const Basic: Story = {args: {}};
