# Blue Agents (Blue 에이전트)

There aren't any specialist blue agents in CC4 - they are for you to make!

> CC4(CAGE Challenge 4)에는 전용으로 만들어진 Blue 에이전트(방어 측 에이전트)가
> 따로 없습니다. 직접 만들어 보는 것이 이 챌린지의 목표입니다!

However there are some basic agent that can be useful:

> 다만 기본적으로 제공되어 유용하게 쓸 수 있는 몇 가지 에이전트가 있습니다.

## Constant Agent (상수 에이전트)
::: CybORG.Agents.SimpleAgents.ConstantAgent.ConstantAgent
    handler: python
    options:
        show_source: false
        show_root_heading: false
        heading_level: 3
        show_category_heading: true
        docstring_style: "numpy"
        show_if_no_docstring: false
        show_docstring_parameters: true

## Sleep Agent (휴면 에이전트)
::: CybORG.Agents.SimpleAgents.ConstantAgent.SleepAgent
    handler: python
    options:
        show_source: false
        show_root_heading: false
        heading_level: 3
        show_category_heading: false
        docstring_style: "numpy"
        show_if_no_docstring: false
        show_docstring_parameters: true