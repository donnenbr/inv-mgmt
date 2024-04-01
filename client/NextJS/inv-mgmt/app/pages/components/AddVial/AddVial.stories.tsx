import React from 'react';
import type {Meta, StoryObj} from '@storybook/react';

import {AddVial} from './AddVial';

const meta: Meta<typeof AddVial> = {
  component: AddVial,
};

export default meta;

type Story = StoryObj<typeof AddVial>;

export const Basic: Story = {args: {}};
