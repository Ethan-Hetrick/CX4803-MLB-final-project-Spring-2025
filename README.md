# Machine Learning Models Trained on Frequency Chaos Game Representations Enable Subspecies-Level Prediction of *Salmonella enterica*

*Final Project for Machine Learning in Computational Biology CSE7850/CX4803-MLB at Georgia Institute of Technology*

## Abstract

As Next-Generation Sequencing data continues to grow at an exponential rate, scalable methods for genome comparison are in high-demand. For example, public health surveillance and environmental monitoring laboratories routinely query large sequence database for organism identification. However, traditional sequence alignment algorithms have become infeasible for querying at the current scale. Consequently, alignment-free sequence identification methods have gained traction in recent years. However, the heuristic methods which improve scalability typically lack high-resolution at the subspecies or strain-level, and still often run into scaling issues given their underlying data structures and algorithm time-complexity. Here, I apply **Frequency Chaos Game Representations (FCGRs)** to encode genome assembly *k-mer* counts into compact 2D matrices, providing light-weight genome representations. Using *Salmonella enterica* as a model organism, I demonstrate that simple machine learning algorithms can accurately predict subspecies and strain-level classifcations from FCGR-encoded genomes.

## Introduction

Historically, *Salmonella enterica* have been subtyped using a variety of *in vitro* methods including but not limited to biochemical, antigen identification, and PCR assays using subtype-specific primers. With the advent of Next-Generation Sequencing, laboratories have started to transition to *in silico* methods for subtyping. What all of the `in silico` methods have in common is they use sequence alignment reference sequences. These typically include high-quality genome references, alleles, or antigen encoding genes. For species-level, and more recently, subspecies-level identification, Average Nucleotide Identity (ANI) thresholds of 95% and 98%, respectively, are routinely used.

## Methods

### Data Curation

### Preprocessing

### Architectures

## Citations

