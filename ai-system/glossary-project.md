# Glossary — Project Documentation Terms

Status: Draft

## Product Vision

A document describing why the product exists, who it is for, what problem it solves, MVP scope and success criteria.

## PRD

Product Requirements Document.

The main requirements document for the product.

## User Story

A feature description from the user's perspective.

Format:

```text
As a [role], I want [action], so that [value].
```

## Acceptance Criteria

Conditions that must be true for a task or feature to be accepted.

## Backlog

The ordered list of work items.

Contains epics, features, tasks, bugs, improvements, priorities, dependencies and statuses.

## Goal

A high-level project or system outcome that explains why work matters.

Goals are planning context. They do not authorize execution by themselves.

## Initiative

A planning container under a goal.

An initiative groups related epics and tasks that contribute to the same outcome.

Initiatives are not executable units.

## Epic

A planning container under an initiative.

An epic groups related tasks that together deliver a coherent capability, documentation outcome, governance improvement or technical result.

Epics are not executable units.

## Feature

A product capability that gives user or business value.

## Task

A concrete executable unit of work.

Tasks may optionally reference an initiative and epic, but execution authority still comes from task approval, scope and acceptance criteria.

## Agent Work Package

A child planning unit under a parent task.

An Agent Work Package describes one role or executor contribution, but it does not authorize execution by itself.

## Scope

What is included in a task.

## Out of Scope

What is explicitly excluded from a task.

This prevents uncontrolled expansion and unnecessary implementation.

## Scope Creep

Uncontrolled growth of the task or project scope.

Example: a task asks for login, but implementation adds registration, roles and refresh tokens without approval.

## MVP

Minimum Viable Product.

The smallest useful version of the product that solves the core user problem.

## Architecture Document

A document describing technical structure, stack, modules, data model, API, security and risks.

## API Documentation

A document describing API contracts: endpoints, methods, request body, response body, status codes, errors and authorization rules.

## Database Schema

A document describing tables, fields, types, relations, indexes and constraints.

## UX Specification

A document describing screens, flows, UI elements, states, errors and empty states.

## Test Plan

A document describing testing strategy, test cases, positive scenarios, negative scenarios, edge cases and regression checks.

## ADR

Architecture Decision Record.

A document that records an important architecture decision.

## Deployment Guide

A document describing how the application is deployed and operated.

## Changelog

A document recording project changes by version or date.
