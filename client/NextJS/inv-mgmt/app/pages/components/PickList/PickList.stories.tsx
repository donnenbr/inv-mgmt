import React from 'react';
import type {Meta, StoryObj} from '@storybook/react';

import {PickList} from './PickList';

const meta: Meta<typeof PickList> = {
  component: PickList,
};

export default meta;

type Story = StoryObj<typeof PickList>;

export const Basic: Story = {args: {}};
