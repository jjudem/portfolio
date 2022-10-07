# [Automated AWS + Venafi certificate renewals](https://github.com/jjudem/portfolio/tree/main/AWS%20-%20Automated%20Certificate%20Renewal)
An unsupervised Venafi certificate management for AWS Cloudfront, Loadbalancer, and S3 that supports multiple actions such as Certificate Renewals, Certificate Retrievals, Certificate Request to Creation, OPENSSL commands to Certificate, and uploading of certificate to AWS Certificate Manager, and Certificate Validation.
* Removed the manual process of managing hundereds to thousands of certificates that is use across multiple environments and applications
* Developed using Python, AWS CLI, Venafi API Integrations that runs 
* Runs on a scheduled Jenkins Pipeline or can be run in-demand for creation and retrieval

# [AWS post-patching checks](https://github.com/jjudem/portfolio/tree/main/AWS%20-%20Postpatching%20Checks)
* Automated check for AWS Target groups, AWS Auto scaling groups, Service after monthly patching 
* Integrated using AWS CLI, Python, and Jenkins Pipeline

# [CUPS - Self-healing scripts](https://github.com/jjudem/portfolio/tree/main/Bash%20-%20CUPS%20health%20check)
* Developed to have unsupervised checks on [CUPS Printers](https://www.cups.org/), to promote self-healing on software issues such as unreachable printers, stopped printers
* Self healing bash scripts and incident tracking for CUPS Printers under one network 
* Script can be scheduled via CRON, Jenkins Pipeline, or any CI/CD tool that can have a Linux as an agent
